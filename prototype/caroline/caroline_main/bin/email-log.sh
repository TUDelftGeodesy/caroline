#!/bin/bash

DATE=$(date -d 'yesterday 12:00' '+%Y-%m-%d')

echo "The following CAROLINE processes were logged on ${DATE}:

----------------

$(grep ${DATE} /project/caroline/Software/caroline-prototype*/work/submitted_jobs.log | cut -d: -f2- | cut -dT -f2-)

----------------" | mailx -s "CAROLINE log ${DATE}" s.a.n.vandiepen@tudelft.nl