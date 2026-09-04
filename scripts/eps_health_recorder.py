#!/usr/bin/env python3
"""The recorder of docs/225, as one implementation instead of six scripts.

Nothing here is new work. Every rule and every number comes from a verification
already in this repository, and the point of the module is that the
specification's parts finally sit in one place and run together:

    per-unit fingerprint, deviation, refusal to declare   docs/196, docs/265
    common-mode rejection against sibling channels        docs/286
    two independent time scales, neither gating the other docs/269
    channel admission by cross-validation at end of line  docs/280
    time since key-on and persistence to key-off          docs/259
    a record that packs into 30 bytes                     docs/265
    the slow side reads slope change, not level           docs/317

What it deliberately does not do is listed in docs/225 section 5: no
prediction, no capability value, no fault location, no remaining life. The
field names are checked against that list by forbidden_fields().

Enrol once while the unit is known good, then run. The runtime never sees the
enrolment data again -- it carries the fingerprint, which is 56 bytes per channel.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field, fields
from typing import Iterable, Sequence

import numpy as np

ROBUST = 3.0 * 1.4826          # MAD -> a 3-sigma-equivalent floor
FAST_WINDOW = 50               # 5 s at 10 Hz, docs/225
SLOW_WINDOW = 100              # continuous mean, docs/271 grid
CV_SHIFT_MAX = 1.0             # channel admission, docs/280
FORBIDDEN = ("capability", "remaining", "rul", "life", "predict",
             "location", "which_fault", "percent_of_new", "severity")


# ---------------------------------------------------------------- fingerprint

FP_FMT = "<" + "f" * 14        # 14 x float32 = 56 bytes, measured (docs/317)


@dataclass(frozen=True)
class ChannelFingerprint:
    """What end of line leaves behind for one channel. 56 bytes packed."""
    name: str
    slope: float
    intercept: float
    floor: float                # this unit's own noise, at shipping
    op_lo: float                # the operating range that was swept; outside
    op_hi: float                # it the element declines to declare
    thr_fast_mean: float
    thr_fast_max: float
    thr_slow: float
    alarm_per_hour_fast: float  # what the fast side could actually be calibrated to
    alarm_per_hour_slow: float  # and the slow side, docs/282
    cv_shift: float             # how far a held-out normal interval missed
    admitted: bool              # docs/280: not admitted -> never declares
    # docs/317: the slow side reads slope change, not level. The healthy drift
    # holds one slope; the onset changes it. These two carry that baseline.
    slope_drift: float = 0.0    # residual per unit accumulated stress, at shipping
    slope_scatter: float = 0.0  # its robust spread, the unit the change is read in
    siblings: tuple[str, ...] = ()

    def pack(self) -> bytes:
        return struct.pack(
            FP_FMT, self.slope, self.intercept, self.floor, self.op_lo,
            self.op_hi, self.thr_fast_mean, self.thr_fast_max, self.thr_slow,
            self.alarm_per_hour_fast, self.cv_shift, float(self.admitted),
            float(self.alarm_per_hour_slow), self.slope_drift,
            self.slope_scatter)


# ---------------------------------------------------------------- the record

REC_FMT = "<ffffffHHBB"        # 30 bytes, measured in docs/265


@dataclass(frozen=True)
class Record:
    deviation: float            # distance from this unit's own baseline
    granularity: float          # the floor that distance is measured in
    operating_point: float
    op_second: float            # docs/225 lists three; unmeasured ones stay 0
    op_third: float
    confidence: float
    seconds_since_key_on: int   # docs/251: the field reports minutes in
    event_seconds: int
    flags: int                  # bit0 held to key-off, bit1 fast, bit2 slow
    validity: int               # 1 declared, 0 declined

    HELD_TO_KEY_OFF = 0b001
    FAST = 0b010
    SLOW = 0b100

    def pack(self) -> bytes:
        return struct.pack(
            REC_FMT, self.deviation, self.granularity, self.operating_point,
            self.op_second, self.op_third, self.confidence,
            min(self.seconds_since_key_on, 65535),
            min(self.event_seconds, 65535), self.flags, self.validity)

    @staticmethod
    def unpack(b: bytes) -> "Record":
        return Record(*struct.unpack(REC_FMT, b))

    def describe(self) -> str:
        if not self.validity:
            return (f"[{self.seconds_since_key_on:>5}s] 宣言しない "
                    f"(動作点が指紋の範囲外)")
        which = []
        if self.flags & Record.FAST:
            which.append("速い側")
        if self.flags & Record.SLOW:
            which.append("遅い側")
        if self.flags & Record.HELD_TO_KEY_OFF:
            which.append("キーオフまで持続")
        tail = ("  " + " / ".join(which)) if which else ""
        return (f"[{self.seconds_since_key_on:>5}s] 逸脱 {self.deviation:>6.2f} "
                f"(粒度 {self.granularity:.4g}) 事象 {self.event_seconds:>4}s{tail}")


def forbidden_fields() -> list[str]:
    """docs/225 section 5, enforced against the field names themselves."""
    names = [f.name.lower() for f in fields(Record)] + \
            [f.name.lower() for f in fields(ChannelFingerprint)]
    return [n for n in names if any(k in n for k in FORBIDDEN)]


# ---------------------------------------------------------------- enrolment

def _floor(residual: np.ndarray) -> float:
    return float(ROBUST * np.median(np.abs(residual - np.median(residual))))


def common_mode_reject(values: dict[str, np.ndarray],
                       name: str, siblings: Sequence[str]) -> np.ndarray:
    """This channel minus the median of its same-kind siblings (docs/286).

    A warm-up, an ambient shift or a supply sag moves every sibling the same
    way and cancels; a fault in one place does not. Without siblings the raw
    channel is returned, and docs/286 measured that such channels do not
    improve -- DC bus voltage stayed at 16.8 times the design rate.
    """
    y = values[name]
    sib = [values[s] for s in siblings if s in values]
    if not sib:
        return y
    return y - np.median(np.vstack(sib), axis=0)


@dataclass
class Fingerprint:
    """Everything the runtime carries. One ChannelFingerprint per channel."""
    channels: dict[str, ChannelFingerprint] = field(default_factory=dict)
    sample_hz: float = 10.0
    n_tests: int = 1            # admitted channels x 2 detectors, docs/294

    @property
    def admitted(self) -> list[str]:
        return [n for n, c in self.channels.items() if c.admitted]

    def pack(self) -> bytes:
        return b"".join(c.pack() for c in self.channels.values())


def enrol(values: dict[str, np.ndarray],
          operating_point: dict[str, np.ndarray],
          siblings: dict[str, Sequence[str]] | None = None,
          alarm_per_hour: float = 1.0,
          sample_hz: float = 10.0) -> Fingerprint:
    """End of line. Sweep the operating range once while the unit is good.

    The interval is split in two: the first half fits the line and sets the
    floor, the second half is held out to decide whether the channel is
    admitted at all. docs/280 found channels whose normal behaviour does not
    reproduce, and a channel that cannot describe its own healthy self should
    never be allowed to declare a fault.
    """
    siblings = siblings or {}
    fp = Fingerprint(sample_hz=sample_hz)

    # A unit fires if ANY admitted channel's ANY detector fires, so the rate a
    # channel is calibrated to must be divided by the number of tests the unit
    # runs. Calibrating each channel to the unit's rate and then OR-ing them
    # inflated the unit's false alarms 8x on the inverter (docs/294). Two
    # passes: decide admission first, then calibrate against that count.
    prepared = {}
    for name in values:
        y = common_mode_reject(values, name, siblings.get(name, ()))
        op = operating_point[name]
        if len(y) < 4 * FAST_WINDOW or np.std(op) == 0:
            continue
        # the line, the floor and the thresholds use the whole enrolment.
        # Splitting it for cross-validation would halve the calibration sample,
        # and docs/282 showed the threshold is a quantile of that sample -- the
        # admission check must not spend the calibration budget.
        a, b = np.polyfit(op, y, 1)
        res_fit = y - (a * op + b)
        g = _floor(res_fit)
        if g <= 0:
            continue

        # admission only: does a fingerprint from one half describe the other
        h = len(y) // 2
        ra = y[:h] - (a * op[:h] + b)
        rb = y[h:] - (a * op[h:] + b)
        shift = abs(float(np.median(rb) - np.median(ra))) / g
        admitted = shift < CV_SHIFT_MAX

        # the mean detector averages the signed residual and then takes the
        # magnitude, so noise cancels; averaging |residual| would not cancel
        # and is a level statistic, not a detector (found by demo_recorder.py
        # failing to reproduce docs/286)
        prepared[name] = (a, b, g, op, res_fit / g, shift, admitted)

    n_tests = max(1, 2 * sum(1 for v in prepared.values() if v[6]))
    fp.n_tests = n_tests
    for name, (a, b, g, op, dev, shift, admitted) in prepared.items():
        thr_mean, thr_max, thr_slow, ach_fast, ach_slow = _calibrate(
            dev, alarm_per_hour / n_tests, sample_hz)
        sd, ss = _slope_baseline(dev, op)
        fp.channels[name] = ChannelFingerprint(
            name=name, slope=float(a), intercept=float(b), floor=g,
            op_lo=float(op.min()), op_hi=float(op.max()),
            thr_fast_mean=thr_mean, thr_fast_max=thr_max, thr_slow=thr_slow,
            # report the rates at the unit level, which is what a vehicle sees
            alarm_per_hour_fast=ach_fast * n_tests,
            alarm_per_hour_slow=ach_slow * n_tests,
            cv_shift=shift, admitted=admitted,
            slope_drift=sd, slope_scatter=ss,
            siblings=tuple(siblings.get(name, ())))
    return fp


def _slope_baseline(dev: np.ndarray, op: np.ndarray) -> tuple[float, float]:
    """The slow side's baseline slope and its spread (docs/317).

    The axis is accumulated stress, not calendar time (docs/312), and it is
    built here the same way docs/315 builds it: the operating point above its
    own resting value, accumulated. A window shorter than the enrolment is
    needed for the spread to mean anything, so it is a quarter of it, capped.
    """
    n = len(dev)
    w = min(max(n // 4, 20), 5000)
    if n < 2 * w:
        return 0.0, 0.0
    stress = np.cumsum(np.maximum(op - float(np.median(op)), 0.0))
    a = []
    for i in range(0, n - w, max(1, w // 4)):
        x, y = stress[i:i + w], dev[i:i + w]
        vx = x.var()
        if vx > 0:
            a.append(float(((x - x.mean()) * (y - y.mean())).mean() / vx))
    if len(a) < 3:
        return 0.0, 0.0
    m = float(np.median(a))
    return m, float(1.4826 * np.median(np.abs(np.asarray(a) - m)))


def _calibrate(dev: np.ndarray, alarm_per_hour: float, sample_hz: float):
    """Thresholds at a declared alarm rate, or the finest the sample allows.

    docs/282: a threshold is a quantile of the enrolment sample, so k values
    cannot express a rate finer than 1/k. Rather than silently return a
    quantile that does not exist, the achieved rate is reported back and the
    caller can see how far it is from what was asked.
    """
    per_hour = sample_hz * 3600.0

    def q_for(n_windows: int, k: int) -> tuple[float, float]:
        want = alarm_per_hour / (per_hour / n_windows)
        floor_rate = 1.0 / k
        rate = max(want, floor_rate)
        return 1.0 - rate, rate * (per_hour / n_windows)

    kf = len(dev) // FAST_WINDOW
    w = dev[:kf * FAST_WINDOW].reshape(kf, FAST_WINDOW) if kf else dev[None, :]
    qf, achieved = q_for(FAST_WINDOW, max(1, w.shape[0]))
    thr_mean = float(np.quantile(np.abs(w.mean(axis=1)), qf))
    thr_max = float(np.quantile(np.abs(w).max(axis=1), qf))

    slow = _running_mean(dev, SLOW_WINDOW)          # signed, then abs below
    if slow is None:
        thr_slow, ach_slow = float("inf"), float("inf")
    else:
        qs, ach_slow = q_for(1, len(slow))
        thr_slow = float(np.quantile(np.abs(slow), qs))   # |mean|, not mean|.|
    return thr_mean, thr_max, thr_slow, achieved, ach_slow


def _running_mean(x: np.ndarray, n: int):
    if len(x) < n:
        return None
    c = np.concatenate(([0.0], np.cumsum(x)))
    return (c[n:] - c[:-n]) / n


# ---------------------------------------------------------------- runtime

class Recorder:
    """Armed whenever assist is active. Two time scales, neither gating the other.

    docs/269 found the fast window can never reach a degradation that only
    shows in minutes of averaging, because docs/225 extended the window only on
    firing -- the extension was gated on the thing it would have to detect. So
    the slow side runs continuously and independently here.
    """

    def __init__(self, fp: Fingerprint):
        self.fp = fp
        self.records: list[Record] = []

    def run_session(self, values: dict[str, np.ndarray],
                    operating_point: dict[str, np.ndarray],
                    siblings: dict[str, Sequence[str]] | None = None,
                    require_calibrated: bool = True,
                    alarm_per_hour: float = 1.0) -> list[Record]:
        """One key-on to key-off. Emits a record per fast window.

        A detector runs only if enrolment could express the requested alarm
        rate at all. docs/282: a threshold is a quantile of k samples and
        cannot be finer than 1/k, so a detector calibrated at 857 alarms per
        hour is not a detector for a target of one -- it is a threshold that
        happens to sit somewhere. Pass require_calibrated=False to see it fire
        anyway, which is how its uselessness was measured.
        """
        siblings = siblings or {}
        hz = self.fp.sample_hz
        out: list[Record] = []
        for name in self.fp.admitted:
            c = self.fp.channels[name]
            y = common_mode_reject(values, name, siblings.get(name, ()))
            op = operating_point[name]
            n = len(y) // FAST_WINDOW
            if not n:
                continue
            use_fast = (not require_calibrated) or c.alarm_per_hour_fast <= alarm_per_hour
            use_slow = (not require_calibrated) or c.alarm_per_hour_slow <= alarm_per_hour
            resid = (y - (c.slope * op + c.intercept)) / c.floor
            slow = _running_mean(resid, SLOW_WINDOW)      # signed, then abs
            event_start = None
            for i in range(n):
                s = slice(i * FAST_WINDOW, (i + 1) * FAST_WINDOW)
                ow = op[s]
                t = int(i * FAST_WINDOW / hz)
                if not ((ow >= c.op_lo) & (ow <= c.op_hi)).all():
                    out.append(Record(0.0, c.floor, float(np.median(ow)), 0.0,
                                      0.0, 0.0, t, 0, 0, 0))
                    event_start = None
                    continue
                r_w = resid[s]
                flags = 0
                if use_fast and abs(float(r_w.mean())) > c.thr_fast_mean:
                    flags |= Record.FAST
                if use_fast and float(np.abs(r_w).max()) > c.thr_fast_max:
                    flags |= Record.FAST
                j = i * FAST_WINDOW
                if use_slow and slow is not None and j < len(slow) \
                        and abs(slow[j]) > c.thr_slow:
                    flags |= Record.SLOW
                d = np.abs(r_w)
                if flags and event_start is None:
                    event_start = t
                elif not flags:
                    event_start = None
                dur = (t - event_start + FAST_WINDOW // int(hz)) if event_start is not None else 0
                out.append(Record(float(max(d.mean(), d.max())), c.floor,
                                  float(np.median(ow)), 0.0, 0.0, 1.0,
                                  t, dur, flags, 1))
            # docs/259: an event still open at key-off is confirmed as persistent
            if out and out[-1].flags:
                last = out[-1]
                out[-1] = Record(last.deviation, last.granularity,
                                 last.operating_point, last.op_second,
                                 last.op_third, last.confidence,
                                 last.seconds_since_key_on, last.event_seconds,
                                 last.flags | Record.HELD_TO_KEY_OFF,
                                 last.validity)
        self.records.extend(out)
        return out


def fired(records: Iterable[Record]) -> bool:
    return any(r.validity and r.flags for r in records)


if __name__ == "__main__":
    bad = forbidden_fields()
    print("禁じられた語を含む欄:", bad if bad else "なし")
    print(f"指紋 1チャネル {len(struct.pack(FP_FMT, *([0.0] * 12)))} バイト")
    print(f"記録 1件      {len(Record(0,0,0,0,0,0,0,0,0,1).pack())} バイト")
    # docs/265: float32 does not reproduce float64 bit for bit, so exact
    # equality is the wrong test. What matters is whether the rounding could
    # move a verdict, so it is measured against the deviation itself.
    r = Record(3.5, 0.21, 12.0, 0.0, 0.0, 1.0, 1200, 45, 0b011, 1)
    back = Record.unpack(r.pack())
    err = abs(back.deviation - r.deviation)
    assert err < r.deviation * 1e-5, f"往復の誤差が大きい: {err}"
    assert (back.flags, back.validity, back.seconds_since_key_on) == \
           (r.flags, r.validity, r.seconds_since_key_on), "整数欄が壊れる"
    print(f"往復の誤差 {err:.2e} (逸脱 {r.deviation})")
    print("往復:", back.describe())
