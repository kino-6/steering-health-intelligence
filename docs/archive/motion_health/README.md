# Motion health archive

## 状況

このArchiveは、自動運転・商用車両群向けの操舵系運行可否 / 点検優先度判断を探索した結果を閉じるための置き場である。

fleet downtime、診断時間短縮、maintenance schedulingの需要はある。
しかし、EPS/SbWサプライヤが公開情報だけで外販テーマにできる差分は確認できなかった。

必要データはOEM / fleet / platform契約に依存し、既存remote diagnosticsはDTC severity、action plan、API連携、service routingをすでに強く扱っている。

## 最終判断

外販テーマとしては **Stop / Archive** とする。

残す知見は次の通り。

- 操舵系単独より、chassis / motion health bundleとして見た方が市場需要には近い。
- ただし、そのbundleはOEM / fleet / platform側の領域であり、EPS/SbWサプライヤ単独の外販テーマにはしにくい。
- EPS/SbWサプライヤが残せるのは、特定program内での状態説明、診断読み順、service engineering向け補足、field-to-engineering feedbackである。
- 安全保証、運行可否、交換時期予測、root cause断定は主張しない。

## 主要ファイル

- [69 new focus](69_old_theme_archive_and_new_focus.md)
- [75 final decision](75_motion_health_mhq001_final_decision.md)
- [76 other MHQ deep dive](76_other_mhq_20min_deep_dive.md)
- [77 deeper review](77_mhq004_007_008_deeper_review.md)
- [79 archive index](79_motion_health_archive_index.md)

## RDIとの関係

この探索で残った「component-specific explanation」「service outcome feedback」「既存remote diagnosticsとの差分」という論点は、RDI探索へ引き継いだ。
RDIも内部program依存の壁に当たったため、現行条件ではArchiveする。
