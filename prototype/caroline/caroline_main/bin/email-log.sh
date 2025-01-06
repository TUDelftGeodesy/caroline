#!/bin/bash

DATE=$(date -d 'yesterday 12:00' '+%Y-%m-%d')

echo "Subject: CAROLINE log ${DATE}

The following CAROLINE processes were logged on ${DATE}:

----------------

$(grep ${DATE} /project/caroline/Software/caroline-prototype*/work/submitted_jobs.log | cut -d: -f2- | cut -dT -f2-)

----------------" | sendmail s.a.n.vandiepen@tudelft.nl