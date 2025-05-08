# Abbreviations in the squeue

The squeue job name has 8 characters, and is formatted as `JJTTTNNN`. 
Here `JJ` is the two-letter job abbreviation, `TTT` the three-digit track, 
and `NNN` the three-letter area of interest abbreviation.

## Job abbreviations

### Autonomous Coregistered Stack Building module

#### Download submodule

- `SD`: Sentinel-1 Download (for one-time full-period downloads, periodic downloads of the last month are managed by [manage-s1-download.sh](../scripts/manage-s1-download.sh))

#### Coregistration submodule

- `D4`: DeInSAR
- `D5`: Doris v5
- `DC`: Doris v5 cleanup

#### Cropping submodule

- `CR`: crop-to-raw
- `CZ`: crop-to-zarr
- `RE`: Re-SLC (deprecated)

### AAA Job Definition module

None yet

### Contextual Enrichment module

None yet, managed by [contextual-data-definitions.yaml](../config/contextual-data-definitions.yaml) and [manage-contextual-data.sh](../scripts/manage-contextual-data.sh)

### Recursive Parameter Estimation module

#### PSI-batch submodule

- `DE`: DePSI

### Autonomous Analysis module

None yet

### Risk module

None yet

### Interactive Interpretation Interface (Dashboard) module

#### PSI-batch submodule

- `DP`: DePSI-post
- `MR`: Read mrm
- `PU`: Portal upload preparation (the actual upload is managed by [manage-portal-upload.sh](../scripts/manage-portal-upload.sh))
- `TB`: Tarball creation

### Push module

#### Notification submodule

- `EM`: Email

### Logging & library module

None yet

## Area of Interest Abbreviations

### Belgium, Luxembourg, and the Netherlands

- `BLX`: be_lu_nl_benelux

### Greece

- `GST`: gr_santorini

### Iceland

- `IIC`: is_iceland (inactive)

### Indonesia

- `IJC`: id_jakarta_cubic
- `IJL`: id_jakarta_large (inactive)
- `IJQ`: id_jakarta

### Netherlands

- `NAL`: nl_aldeboarn
- `NAM`: nl_amsterdam
- `NAS`: nl_assendelft
- `NAT`: nl_amsterdam_tsx
- `NAX`: nl_amsterdam_extended
- `NGC`: nl_groningen_cubic
- `NGD`: nl_groningen_depsi (deprecated)
- `NGK`: nl_grijpskerk
- `NGN`: nl_groningen
- `NHT`: nl_north_holland_south_tsx
- `NLB`: nl_limburg
- `NLS`: nl_limburg_stack (deprecated)
- `NMT`: nl_marken_tsx
- `NNI`: nl_nieuwolda
- `NSC`: nl_schoonebeek
- `NTA`: TEST_nl_amsterdam (for testing)
- `NVW`: nl_veenweiden
- `NWO`: nl_woerden (inactive)
- `NZE`: nl_zegveld

### Singapore

- `SSG`: sg_singapore