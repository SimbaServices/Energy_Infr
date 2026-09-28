# County appraisal-district endpoint check

Each county appraisal district or parish assessor has a public search endpoint that returns an owner name and a contact (mailing address or phone). A timeout, an empty result, or a GIS layer with no owner field means the request we sent is wrong. Change the host, path, method, account prefix, or form fields and try again until that county's site returns the owner and a contact for the sample account.

## Sample account

The batch JSON has `account.owner_name` and `account.prop_id` or `account.geo_id` or `account.upc`, plus `account.mail_line1` when the copied roll stored one. Use that account. The name on the live site may differ if the roll changed. The response still has to contain an owner name and a mailing address or phone.

Copied databases, read only, on the host `propeval`:

- `/home/propeval/Energy_Infr/db/parcels/minerals.db` table `parcels_tx`
- `/home/propeval/Energy_Infr/db/parcels/ks_minerals.db` table `parcels_ks`
- `/home/propeval/Energy_Infr/db/parcels/nm_minerals.db` table `parcels_nm` (`upc` instead of `geo_id`, no `contact` column)

Do not query Oklahoma or Louisiana. Do not open `ok_minerals.db` or `la_minerals.db`. Do not open the property-evaluation databases. Do not change those files.

## What to request

Texas districts often use one of these. Pick the one that district actually publishes:

- Southwest Data Solutions. GET `https://iswdataclient.azurewebsites.net/webSearchid.aspx?dbkey=DBKEY` (or `https://www.southwestdatasolution.com/webSearchID.aspx?dbkey=DBKEY`). POST the hidden `__VIEWSTATE`, `__VIEWSTATEGENERATOR`, `__PREVIOUSPAGE`, and `__EVENTVALIDATION` back, with `ucSearchID$searchid` set to the account and `ucSearchID$ButtonSearch=Search`. Real property is often prefixed `R`, minerals `N`, personal property `P`.
- True Automation PropAccess, `https://propaccess.trueautomation.com/clientdb/PropertySearch.aspx?cid=ID`.
- Pritchard & Abbott, BIS Client, esearch, or the district's own search URL linked from its site or from the Texas Comptroller appraisal-district directory.

Kansas, New Mexico, Oklahoma, and Louisiana stored URLs are often parcel polygons, not the assessor search. A layer with no owner field is not the endpoint. Find that county assessor's property search and call it.

Make the HTTP call yourself with a normal user agent. A form POST that first GETs the viewstate is a valid server-side request. A browser click is not required.

## Result file

Write one JSON object to the result path named in your assignment. Shape:

```json
{
  "batch": "01",
  "counties": [
    {
      "state": "TX",
      "county": "MIDLAND",
      "county_code": "329",
      "sample_account": "0189033",
      "endpoint": "https://iswdataclient.azurewebsites.net/webSearchid.aspx?dbkey=MIDLANDCAD",
      "method": "POST",
      "form_fields": ["ucSearchID$searchid", "ucSearchID$ButtonSearch"],
      "account_sent": "N0189033",
      "http_status": 200,
      "owner_returned": true,
      "contact_returned": true,
      "owner_excerpt": "short owner name from the response",
      "contact_excerpt": "short mailing address or phone from the response"
    }
  ]
}
```

`owner_returned` and `contact_returned` are true only when that text was in the HTTP body. Leave `owner_excerpt` empty when it was not. Do not invent either value. Do not edit the map application, nginx, or git.
