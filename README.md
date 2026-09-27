# U.S. gas takeaway

## Texas Permian

Lease-level vented and flared gas for the Texas side of the Permian, drawn with EIA pipeline centerlines and the grid tie-in points already in the database.

```bash
python src/download_permian.py
python src/load_permian.py
python -m http.server 8765 --directory web
```

Then open http://127.0.0.1:8765. `download_permian.py` is only needed when the Railroad Commission files in `data/raw/rrc` are missing. `load_permian.py` reads those files plus `db/us_pipelines.sqlite` and writes `permian_leases` and the map files in `web/data`.

The same map is published at https://204.168.132.89:8443. That host already serves SS Property Evaluation on ports 80 and 443 (`propeval.simba.services`, Docker on `127.0.0.1:5050`) and SSH on 2222. This site is a separate nginx root on port 8443 and does not share that process. TLS is a Let's Encrypt certificate for the public IPv4 and IPv6 addresses, valid about six days, renewed by `certbot-energy.timer` from `/etc/letsencrypt-energy`.

`python -m agents` refreshes New Mexico, Colorado, Wyoming, California, South Dakota, North Dakota, Louisiana, Arkansas, and Kansas. For each state it clips the same pipeline, transmission, and tie-in layers used by the Permian view, rebuilds 69 kV interconnection points, and probes that state's public well service for a vented or flared column. Lease circles are drawn only when that column is present. On the host, `energy-agents.timer` runs this on the 1st of each month at 05:10 America/Chicago and copies `web/` to `/var/www/energy`. Lease rows found by a web crawl are stored in `state_leases` inside `db/us_pipelines.sqlite`.

The volume is the single vented-or-flared column on the Form PR tapes posted 2026-09-26. Each lease uses its latest month on that tape. The circle is the centroid of RRC surface wells whose lease name matches the filing. Tie-in points are 230 kV-and-above line midpoints within 3 miles of a gas pipeline midpoint. Points of interconnection are 69 kV-and-above substations and taps in those same counties. `python src/build_pois.py` refreshes `web/data/pois.geojson` from the public substation and transmission-line services. New Mexico is not in this view.

## National database

Public EIA and HIFLD data on U.S. natural gas production, interstate border capacity, planned pipeline projects, Henry Hub and citygate prices, vented and flared gas, county pipeline operators, and the 230 kV-and-above transmission grid. The compiled database is `db/us_pipelines.sqlite`. Raw downloads are in `data/raw`. Notes are in `research`.

## Rebuild the database

```bash
pip install -r requirements.txt
python src/fetch_eia.py
python src/ingest.py
```

`fetch_eia.py` reads an EIA API key from the `EIA_API_KEY` environment variable or from `C:\Users\Sam Parker\Take_Action\eia_api.txt`. The key is not copied into this project. `ingest.py` rebuilds the database from those API responses plus the workbooks and GeoJSON files in `data/raw`.

## What the gap means

Takeaway gap = (dry production − in-state consumption) − interstate border capacity, in Bcf/d.

A positive gap means more gas is produced than the state uses, beyond the border capacity EIA records. LNG exports and intrastate pipelines are not in that capacity number, so Gulf Coast states can show a large gap even when gas is reaching export terminals. EIA does not publish a matching basin takeaway capacity, so there is no basin glut ratio.

Pipeline centerlines are the EIA compilation dated January 2020. Capacity is the 2025 state-to-state table. Projects are the EIA workbook current through July 2026. Transmission lines are the public HIFLD 230 kV-and-above subset.

Vented and flared gas is EIA process VGV for 2024, divided by gross withdrawals. County operator shares assign each centerline to the county that contains the segment midpoint. The public centerline layer barely includes gathering lines, and EIA does not publish gathering capacity at the producer meter.

Citygate minus Henry Hub is a delivered-price gap, not a gathering tariff. `$/MWh/mile` interconnect cost is left empty because the public studies report `$/mile` or `$/MW-mile`, and this database does not turn those into an uncited energy tariff.
