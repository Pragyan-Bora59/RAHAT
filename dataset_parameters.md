# Dataset Parameters Inventory

Here is the exhaustive list of all parameters (fields, columns, and properties) contained within the readable datasets currently in your `datasets/` workspace.

> [!NOTE]
> Files like PDFs, JPEGs, and compressed `.tar.gz`/`.zip` archives do not have tabular/spatial parameters and are thus excluded from this list.

### 🏥 Healthcare (`INDIA_HEALTH_FACILITIES_NIC.geojson`)
- `name`
- `type`
- `place`
- `district`
- `state`
- `source`
- `layer`
- `village_id`
- `source_id`

### 🚓 Police Stations (`INDIA_POLICE_STATIONS.geojson`)
- `state`
- `state_cd`
- `district`
- `district_c`
- `ps`
- `ps_cd`
- `latitude`
- `longitude`

### 👥 Population (`PCA_CDB_1809_F_Census.xls`)
- `State/UTs_Code`
- `District_Code`
- `CD Block_Code`
- `Town/Village_Code`
- `Ward_Code`
- `EB_Code`
- `State/UTs_Name`
- `District_Name`
- `Level`
- `Name`
- `Total/Rural/Urban`
- `No of Households`
- `Total Population Person` (and corresponding `Male`, `Female` columns for all demographics)
- `Population in the age group 0-6`
- `Scheduled Castes population`
- `Scheduled Tribes population`
- `Literates Population`
- `Illiterate Persons`
- `Total Worker Population`
- `Main Working Population`
- `Main Cultivator Population`
- `Main Agricultural Labourers Population`
- `Main Household Industries Population`
- `Main Other Workers Population`
- `Marginal Worker Population` (and breakdowns for Cultivator, Agricultural Labourers, Household Industries, Other Workers by age groups 3-6 and 0-3)
- `Non Working Population`

### 🌉 Roads & Infrastructure: Bridges (`SOI_Bridges.parquet`)
- `OBJECTID_12`, `objectid`, `orig_fid`, `objectid_1`
- `fid_bridge`, `unique_id`, `soi_code`, `soi_code_1`
- `name`
- `along_type`, `upon_type`
- `length_m`, `width_m`
- `brige_mtrl`
- `spans_no`
- `svy_date`, `entity_on`
- `gmrotation`, `addl_info`, `photograph`, `remarks`, `remarks_1`
- `lgd_state_`, `lgd_distri`, `lgd_sub_di`, `lgd_state_code`, `lgd_district_code`, `lgd_sub_dist_code`
- `fid_subdistrict`, `subdivision`, `district`, `state`
- `shape_leng`, `geometry`, `bbox`

### 🛣️ Roads & Infrastructure: Causeways (`SOI_Causeways.parquet`)
- `OBJECTID`
- `fid_causeway`, `unique_id`, `soi_code`
- `type`, `name`, `river_name`
- `length_m`, `width_m`
- `all_weathr`
- `svy_date`
- `addl_info`, `photograph`, `remarks`
- `lgd_state_code`, `lgd_district_code`, `lgd_sub_dist_code`
- `fid_subdistrict`, `subdivision`, `district`, `state`
- `shape_leng`, `shape_le_1`, `shape_le_2`, `shape.STLength()`
- `geometry`, `bbox`

### 🛤️ Roads & Infrastructure: Culverts (`SOI_Culverts.parquet`)
- `objectid`, `orig_fid`, `OBJECTID_12`, `objectid_1`
- `name`
- `material`
- `length_m`, `width_m`
- `restrictns`
- `unique_id`, `soi_code`, `sorce_info`
- `svy_date`, `entity_on`
- `gmrotation`, `photograph`, `addl_info`, `remarks`
- `lgd_state_`, `lgd_distri`, `lgd_sub_di`
- `subdivisio`, `district`, `state`
- `shape_leng`, `geometry`, `bbox`

### ⛰️ Roads & Infrastructure: Passes (`SOI_Passes.parquet`)
- `objectid`, `orig_fid`, `objectid_12`, `objectid_1`
- `pass_name`
- `length_m`, `width_m`
- `surface`
- `unique_id`, `soi_code`
- `svy_date`
- `addl_info`, `photograph`, `gmrotation`, `remarks`
- `lgd_state_code`, `lgd_district_code`, `lgd_sub_dist_code`
- `subdivision`, `district`, `state`
- `geometry`, `bbox`

### 🚗 Roads & Infrastructure: Roads (`SOI_Roads.parquet`)
- `OBJECTID`
- `rd_id`, `unique_id`, `urbpl_code`
- `rd_nm`, `road_name`, `abbr`, `dist_nm`
- `rd_cls`, `road_type`, `level_v`
- `rd_lanes`
- `rd_tp_srf`, `surface`
- `rd_mb`
- `rd_yr_cnt`
- `rd_oneway`
- `el_gnd`, `el_photo`
- `d_source`
- `all_weathr`
- `svy_date`
- `feedback`, `urbanbody`, `layer`, `polyline_f`, `remarks`, `addl_info`, `photograph`, `temp`, `zoom_scale`
- `Shape.STLength()`, `geometry`, `bbox`

### 🌉 Roads & Infrastructure: Viaducts (`SOI_Viaducts.parquet`)
- `objectid`, `orig_fid`, `objectid_12`, `objectid_1`
- `type`
- `unique_id`, `soi_code`
- `svy_date`, `entity_on`
- `gmrotation`, `addl_info`, `remarks`
- `lgd_state_`, `lgd_distri`, `lgd_sub_di`
- `subdivisio`, `district`, `state`
- `shape_leng`, `geometry`, `bbox`

### 📦 Shelters & Resources: Resource Inventory (`current_resource_inventory_updated.csv`)
- `resource_id`
- `resource_type`
- `location`
- `revenue_circle`
- `quantity`
- `capacity`
- `contact_agency`
- `last_updated`
- `source`
