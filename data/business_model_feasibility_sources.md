# Business Model Feasibility Source Notes

このメモは、`business_model_feasibility_100.tsv` の発想元を整理する。
個別企業の事業内容をそのまま複製するのではなく、公開情報から見える市場シグナルと、Repo内のEPS Health Intelligence仮説を組み合わせて100案に展開した。

## Source Signals

- Connected vehicle / SDV platforms increasingly combine OTA, remote diagnostics, edge data collection, remote commands, health monitoring, and predictive maintenance.
- Remote diagnostics and SOVD-style service-oriented diagnostics imply that subsystem health summaries can be consumed through existing or emerging diagnostic channels.
- EPS and electric drive research supports the technical plausibility of anomaly / health indicators around motor current, torque, sensors, friction, thermal stress, and control tracking.
- Recent predictive maintenance critiques emphasize that internal diagnostic signals alone are often insufficient for full predictive claims, which supports the repo's Core vs Optional split.
- For an ECU supplier, OEM fleet data, warranty DB, complaints, road, tire, and regional data should be optional extensions, not initial assumptions.

## Referenced Public Sources

- Sibros connected vehicle platform: https://sibros.tech/
- Carota OTA / remote diagnostics: https://w.carota.ai/
- ElectRay FOTA / vehicle state monitoring: https://www.electraytech.com/fota-solution/
- Excelfore connected automotive / diagnostics: https://excelfore.com/
- Excelfore eSync OTA and data gathering: https://excelfore.com/esync-ota
- Bytebeam vehicle health diagnostics: https://www.bytebeam.io/connected-vehicle
- ACTIA remote vehicle condition monitoring: https://www.actiaus.com/solutions/oem-telematics/
- ASAM SOVD: https://www.asam.net/standards/detail/sovd/
- ISO 17978-3 SOVD API: https://www.iso.org/standard/86587.html
- EPS anomaly detection research: https://pmc.ncbi.nlm.nih.gov/articles/PMC9699008/
- EPS multiple degradation design research: https://academic.oup.com/jcde/article/11/4/1/7693726
- Automotive electric drive monitoring review: https://www.mdpi.com/2079-9292/14/19/3950
- EPS rack-driving motor fault estimation: https://www.mdpi.com/2079-9292/11/24/4149
- AI predictive maintenance critique for connected vehicles: https://arxiv.org/abs/2603.13343
- NHTSA EPS functional safety report: https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/13501_812575_electricpowersteeringreport.pdf
