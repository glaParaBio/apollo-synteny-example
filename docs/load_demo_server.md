<!-- vim-markdown-toc GFM -->

* [Copy reference genomes and evidence to Apollo server](#copy-reference-genomes-and-evidence-to-apollo-server)
* [Add assemblies](#add-assemblies)
* [Add evidence tracks](#add-evidence-tracks)
* [Import annotation](#import-annotation)
* [Visualise tracks](#visualise-tracks)

<!-- vim-markdown-toc -->

These instructions assume you have prepared data files as per
[prepare_data.md](prepare_data.md) and you are at the root of the repository, *i.e.*:

```
cd /path/to/apollo-synteny-example
```

# Copy reference genomes and evidence to Apollo server

```
INSTANCE_ID=i-0c7...ba3
dns=`aws ec2 describe-instances --instance-ids ${INSTANCE_ID} --query "Reservations[0].Instances[0].PublicDnsName" --output text`

scp data/trichuris* ec2-user@${dns}:~/data/
scp jbrowse_data/* ec2-user@${dns}:~/deployment/data-staging/
```

# Add assemblies

```
aws ec2-instance-connect ssh --instance-id ${INSTANCE_ID}

function apollo() {
docker\
    run \
    --rm \
    --interactive \
    --tty \
    --add-host host.docker.internal=host-gateway \
    --volume /home/ec2-user/.config/apollo-cli:/root/.config/apollo-cli \
    --volume /home/ec2-user/data:/data \
    --env APOLLO_PROFILE=staging \
    ghcr.io/gmod/apollo-cli:dev \
    "$@"
}
apollo login --force

for x in data/trichuris_muris.PRJEB126.WBPS19.genomic_softmasked.fa.gz \
    data/trichuris_suis.PRJNA179528.WBPS19.genomic_softmasked.fa.gz \
    data/trichuris_trichiura.PRJEB535.WBPS19.genomic_softmasked.fa.gz
do
    fn=`basename $x`
    asm=${fn/.*/}
    asm=${asm/_/ }
    asm=${asm/t/T}

    apollo assembly add-from-fasta --force /data/${fn} --assembly "${asm}"
done
```

# Add evidence tracks

If jbrowse is not already installed:

```
npm install -g  @jbrowse/cli
jbrowse --version
@jbrowse/cli version 3.7.0
```

```
MURIS_ID=$(
  apollo assembly get |
    jq --raw-output '.[] | select(.name=="Trichuris muris")._id'
)
SUIS_ID=$(
  apollo assembly get |
    jq --raw-output '.[] | select(.name=="Trichuris suis")._id'
)
TRICHIURA_ID=$(
  apollo assembly get |
    jq --raw-output '.[] | select(.name=="Trichuris trichiura")._id'
)

apollo jbrowse get-config > data/config.json

jbrowse add-track \
  data/T_suis-1.0_Cont18_vs_TMUE_LG2.paf \
  --load inPlace \
  --name "T. suis vs T. muris TBLASTX" \
  --assemblyNames "${SUIS_ID}","${MURIS_ID}" \
  --force \
  --out data/config.json

jbrowse add-track \
  data/TTRE_chr2_vs_TMUE_LG2.paf \
  --load inPlace \
  --name "T. trichiura vs T. muris TBLASTX" \
  --assemblyNames "${TRICHIURA_ID}","${MURIS_ID}" \
  --force \
  --out data/config.json

## GFF Annotation
jbrowse add-track \
  data/trichuris_muris.PRJEB126.WBPS19.annotations.gff3 \
  --load inPlace \
  --name "T. muris GFF3" \
  --assemblyNames "${MURIS_ID}" \
  --force \
  --out data/config.json

jbrowse add-track \
  data/trichuris_suis.PRJNA179528.WBPS19.annotations.gff3 \
  --load inPlace \
  --name "T. suis GFF3" \
  --assemblyNames "${SUIS_ID}" \
  --force \
  --out data/config.json


## Evidence bam
jbrowse add-track \
  data/TTRE_all_isoseq.chr2.bam \
  --load inPlace \
  --name "T. trichiura ISOseq" \
  --assemblyNames "${TRICHIURA_ID}" \
  --force \
  --out data/config.json

apollo jbrowse set-config /data/config.json
rm data/config.json
```

# Import annotation

This may take about 1/2 hour - 1 hour:

```
apollo feature import \
    --assembly "Trichuris trichiura" \
    --delete-existing \
    /data/trichuris_trichiura.PRJEB535.WBPS19.annotations.gff3
```

# Visualise tracks

Go to the [Apollo demo instance](https://demo-staging.apollo.jbrowse.org) and follow the same steps as for the [local demo](load_local_apollo.md#visualise-tracks)
