from __future__ import annotations
import pytest
from predicTCR_server import create_app
import shutil
import flask
import io
import os
import sys
import pathlib
import smtplib

# add tests helpers package location to path so tests can import gui_test_utils
sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))

import flask_test_utils as ftu


@pytest.fixture()
def app(monkeypatch, tmp_path):
    monkeypatch.setenv("JWT_SECRET_KEY", "abcdefghijklmnopqrstuvwxyz")
    monkeypatch.setattr(
        smtplib.SMTP,
        "__init__",
        lambda self, host: print(f"Monkeypatched SMTP host: {host}", flush=True),
    )
    monkeypatch.setattr(
        smtplib.SMTP,
        "send_message",
        lambda self, msg: flask.current_app.config.update(
            TESTING_ONLY_LAST_SMTP_MESSAGE=msg
        ),
    )
    temp_data_path = str(tmp_path)
    app = create_app(data_path=temp_data_path)
    ftu.add_test_users(app)
    ftu.add_test_samples(app, tmp_path)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def result_zipfile(tmp_path) -> pathlib.Path:
    # make a results zip file with files a.txt, b.txt, c.txt, email.txt
    results_zipfile_contents = tmp_path / "results_zipfile"
    results_zipfile_contents.mkdir()
    result_files = ["a.txt", "b.txt", "c.txt"]
    for result_file in result_files:
        with open(results_zipfile_contents / result_file, "w") as f:
            f.write(f"test file named {result_file}")
    with open(results_zipfile_contents / "email.txt", "w") as f:
        f.write("\n".join(["c.txt", "a.txt", "idontexist.txt"]))
    result_zipfile = pathlib.Path(
        shutil.make_archive(
            f"{tmp_path}/result_zipfile", "zip", results_zipfile_contents
        )
    )
    yield result_zipfile


@pytest.fixture()
def ref_seq_embl() -> io.BytesIO:
    # http://scikit-bio.org/docs/0.5.3/generated/skbio.io.format.embl.html
    embl_str = b"""
ID   X56734; SV 1; linear; mRNA; STD; PLN; 1859 BP.
XX
AC   X56734; S46826;
XX
DT   12-SEP-1991 (Rel. 29, Created)
DT   25-NOV-2005 (Rel. 85, Last updated, Version 11)
XX
DE   Trifolium repens mRNA for non-cyanogenic beta-glucosidase
XX
KW   beta-glucosidase.
XX
OS   Trifolium repens (white clover)
OC   Eukaryota; Viridiplantae; Streptophyta; Embryophyta; Tracheophyta;
OC   Spermatophyta; Magnoliophyta; eudicotyledons; Gunneridae;
OC   Pentapetalae; rosids; fabids; Fabales; Fabaceae; Papilionoideae;
OC   Trifolieae; Trifolium.
XX
RN   [5]
RP   1-1859
RX   DOI; 10.1007/BF00039495.
RX   PUBMED; 1907511.
RA   Oxtoby E., Dunn M.A., Pancoro A., Hughes M.A.;
RT   "Nucleotide and derived amino acid sequence of the cyanogenic
RT   beta-glucosidase (linamarase) from white clover
RT   (Trifolium repens L.)";
RL   Plant Mol. Biol. 17(2):209-219(1991).
XX
RN   [6]
RP   1-1859
RA   Hughes M.A.;
RT   ;
RL   Submitted (19-NOV-1990) to the INSDC.
RL   Hughes M.A., University of Newcastle Upon Tyne, Medical School,
RL   Newcastle
RL   Upon Tyne, NE2 4HH, UK
XX
DR   MD5; 1e51ca3a5450c43524b9185c236cc5cc.
XX
FH   Key             Location/Qualifiers
FH
FT   source          1..1859
FT                   /organism="Trifolium repens"
FT                   /mol_type="mRNA"
FT                   /clone_lib="lambda gt10"
FT                   /clone="TRE361"
FT                   /tissue_type="leaves"
FT                   /db_xref="taxon:3899"
FT   mRNA            1..1859
FT                   /experiment="experimental evidence, no additional
FT                   details recorded"
FT   CDS             14..1495
FT                   /product="beta-glucosidase"
FT                   /EC_number="3.2.1.21"
FT                   /note="non-cyanogenic"
FT                   /db_xref="GOA:P26204"
FT                   /db_xref="InterPro:IPR001360"
FT                   /db_xref="InterPro:IPR013781"
FT                   /db_xref="InterPro:IPR017853"
FT                   /db_xref="InterPro:IPR033132"
FT                   /db_xref="UniProtKB/Swiss-Prot:P26204"
FT                   /protein_id="CAA40058.1"
FT                   /translation="MDFIVAIFALFVISSFTITSTNAVEASTLLDIGNLSRS
FT                   SFPRGFIFGAGSSAYQFEGAVNEGGRGPSIWDTFTHKYPEKIRDGSNADITV
FT                   DQYHRYKEDVGIMKDQNMDSYRFSISWPRILPKGKLSGGINHEGIKYYNNLI
FT                   NELLANGIQPFVTLFHWDLPQVLEDEYGGFLNSGVINDFRDYTDLCFKEFGD
FT                   RVRYWSTLNEPWVFSNSGYALGTNAPGRCSASNVAKPGDSGTGPYIVTHNQI
FT                   LAHAEAVHVYKTKYQAYQKGKIGITLVSNWLMPLDDNSIPDIKAAERSLDFQ
FT                   FGLFMEQLTTGDYSKSMRRIVKNRLPKFSKFESSLVNGSFDFIGINYYSSSY
FT                   ISNAPSHGNAKPSYSTNPMTNISFEKHGIPLGPRAASIWIYVYPYMFIQEDF
FT                   EIFCYILKINITILQFSITENGMNEFNDATLPVEEALLNTYRIDYYYRHLYY
FT                   IRSAIRAGSNVKGFYAWSFLDCNEWFAGFTVRFGLNFVD"
XX
SQ   Sequence 1859 BP; 609 A; 314 C; 355 G; 581 T; 0 other;
     aaacaaacca aatatggatt ttattgtagc catatttgct ctgtttgtta ttagctcatt
     cacaattact tccacaaatg cagttgaagc ttctactctt cttgacatag gtaacctgag
     tcggagcagt tttcctcgtg gcttcatctt tggtgctgga tcttcagcat accaatttga
     aggtgcagta aacgaaggcg gtagaggacc aagtatttgg gataccttca cccataaata
     tccagaaaaa ataagggatg gaagcaatgc agacatcacg gttgaccaat atcaccgcta
     caaggaagat gttgggatta tgaaggatca aaatatggat tcgtatagat tctcaatctc
     ttggccaaga atactcccaa agggaaagtt gagcggaggc ataaatcacg aaggaatcaa
     atattacaac aaccttatca acgaactatt ggctaacggt atacaaccat ttgtaactct
     ttttcattgg gatcttcccc aagtcttaga agatgagtat ggtggtttct taaactccgg
     tgtaataaat gattttcgag actatacgga tctttgcttc aaggaatttg gagatagagt
     gaggtattgg agtactctaa atgagccatg ggtgtttagc aattctggat atgcactagg
     aacaaatgca ccaggtcgat gttcggcctc caacgtggcc aagcctggtg attctggaac
     aggaccttat atagttacac acaatcaaat tcttgctcat gcagaagctg tacatgtgta
     taagactaaa taccaggcat atcaaaaggg aaagataggc ataacgttgg tatctaactg
     gttaatgcca cttgatgata atagcatacc agatataaag gctgccgaga gatcacttga
     cttccaattt ggattgttta tggaacaatt aacaacagga gattattcta agagcatgcg
     gcgtatagtt aaaaaccgat tacctaagtt ctcaaaattc gaatcaagcc tagtgaatgg
     ttcatttgat tttattggta taaactatta ctcttctagt tatattagca atgccccttc
     acatggcaat gccaaaccca gttactcaac aaatcctatg accaatattt catttgaaaa
     acatgggata cccttaggtc caagggctgc ttcaatttgg atatatgttt atccatatat
     gtttatccaa gaggacttcg agatcttttg ttacatatta aaaataaata taacaatcct
     gcaattttca atcactgaaa atggtatgaa tgaattcaac gatgcaacac ttccagtaga
     agaagctctt ttgaatactt acagaattga ttactattac cgtcacttat actacattcg
     ttctgcaatc agggctggct caaatgtgaa gggtttttac gcatggtcat ttttggactg
     taatgaatgg tttgcaggct ttactgttcg ttttggatta aactttgtag attagaaaga
     tggattaaaa aggtacccta agctttctgc ccaatggtac aagaactttc tcaaaagaaa
     ctagctagta ttattaaaag aactttgtag tagattacag tacatcgttt gaagttgagt
     tggtgcacct aattaaataa aagaggttac tcttaacata tttttaggcc attcgttgtg
     aagttgttag gctgttattt ctattatact atgttgtagt aataagtgca ttgttgtacc
     agaagctatg atcataacta taggttgatc cttcatgtat cagtttgatg ttgagaatac
     tttgaattaa aagtcttttt ttattttttt aaaaaaaaaa aaaaaaaaaa aaaaaaaaa
//
"""
    return io.BytesIO(embl_str)


@pytest.fixture()
def ref_seq_fasta() -> io.BytesIO:
    # http://prodata.swmed.edu/promals/info/fasta_format_file_example.htm
    fasta_str = b"""
>seq0
FQTWEEFSRAAEKLYLADPMKVRVVLKYRHVDGNLCIKVTDDLVCLVYRTDQAQDVKKIEKF
>seq1
KYRTWEEFTRAAEKLYQADPMKVRVVLKYRHCDGNLCIKVTDDVVCLLYRTDQAQDVKKIEKFHSQLMRLME LKVTDNKECLKFKTDQAQEAKKMEKLNNIFFTLM
"""
    return io.BytesIO(fasta_str)


@pytest.fixture()
def ref_seq_genbank() -> io.BytesIO:
    # https://raw.githubusercontent.com/biopython/biopython/master/Doc/examples/ls_orchid.gbk
    gbk_str = b"""
LOCUS       Z78533                   740 bp    DNA     linear   PLN 30-NOV-2006
DEFINITION  C.irapeanum 5.8S rRNA gene and ITS1 and ITS2 DNA.
ACCESSION   Z78533
VERSION     Z78533.1  GI:2765658
KEYWORDS    5.8S ribosomal RNA; 5.8S rRNA gene; internal transcribed spacer;
            ITS1; ITS2.
SOURCE      Cypripedium irapeanum
  ORGANISM  Cypripedium irapeanum
            Eukaryota; Viridiplantae; Streptophyta; Embryophyta; Tracheophyta;
            Spermatophyta; Magnoliophyta; Liliopsida; Asparagales; Orchidaceae;
            Cypripedioideae; Cypripedium.
REFERENCE   1
  AUTHORS   Cox,A.V., Pridgeon,A.M., Albert,V.A. and Chase,M.W.
  TITLE     Phylogenetics of the slipper orchids (Cypripedioideae:
            Orchidaceae): nuclear rDNA ITS sequences
  JOURNAL   Unpublished
REFERENCE   2  (bases 1 to 740)
  AUTHORS   Cox,A.V.
  TITLE     Direct Submission
  JOURNAL   Submitted (19-AUG-1996) Cox A.V., Royal Botanic Gardens, Kew,
            Richmond, Surrey TW9 3AB, UK
FEATURES             Location/Qualifiers
     source          1..740
                     /organism="Cypripedium irapeanum"
                     /mol_type="genomic DNA"
                     /db_xref="taxon:49711"
     misc_feature    1..380
                     /note="internal transcribed spacer 1"
     gene            381..550
                     /gene="5.8S rRNA"
     rRNA            381..550
                     /gene="5.8S rRNA"
                     /product="5.8S ribosomal RNA"
     misc_feature    551..740
                     /note="internal transcribed spacer 2"
ORIGIN
        1 cgtaacaagg tttccgtagg tgaacctgcg gaaggatcat tgatgagacc gtggaataaa
       61 cgatcgagtg aatccggagg accggtgtac tcagctcacc gggggcattg ctcccgtggt
      121 gaccctgatt tgttgttggg ccgcctcggg agcgtccatg gcgggtttga acctctagcc
      181 cggcgcagtt tgggcgccaa gccatatgaa agcatcaccg gcgaatggca ttgtcttccc
      241 caaaacccgg agcggcggcg tgctgtcgcg tgcccaatga attttgatga ctctcgcaaa
      301 cgggaatctt ggctctttgc atcggatgga aggacgcagc gaaatgcgat aagtggtgtg
      361 aattgcaaga tcccgtgaac catcgagtct tttgaacgca agttgcgccc gaggccatca
      421 ggctaagggc acgcctgctt gggcgtcgcg cttcgtctct ctcctgccaa tgcttgcccg
      481 gcatacagcc aggccggcgt ggtgcggatg tgaaagattg gccccttgtg cctaggtgcg
      541 gcgggtccaa gagctggtgt tttgatggcc cggaacccgg caagaggtgg acggatgctg
      601 gcagcagctg ccgtgcgaat cccccatgtt gtcgtgcttg tcggacaggc aggagaaccc
      661 ttccgaaccc caatggaggg cggttgaccg ccattcggat gtgaccccag gtcaggcggg
      721 ggcacccgct gagtttacgc
//
LOCUS       Z78532                   753 bp    DNA     linear   PLN 30-NOV-2006
DEFINITION  C.californicum 5.8S rRNA gene and ITS1 and ITS2 DNA.
ACCESSION   Z78532
VERSION     Z78532.1  GI:2765657
KEYWORDS    5.8S ribosomal RNA; 5.8S rRNA gene; internal transcribed spacer;
            ITS1; ITS2.
SOURCE      Cypripedium californicum
  ORGANISM  Cypripedium californicum
            Eukaryota; Viridiplantae; Streptophyta; Embryophyta; Tracheophyta;
            Spermatophyta; Magnoliophyta; Liliopsida; Asparagales; Orchidaceae;
            Cypripedioideae; Cypripedium.
REFERENCE   1
  AUTHORS   Cox,A.V., Pridgeon,A.M., Albert,V.A. and Chase,M.W.
  TITLE     Phylogenetics of the slipper orchids (Cypripedioideae:
            Orchidaceae): nuclear rDNA ITS sequences
  JOURNAL   Unpublished
REFERENCE   2  (bases 1 to 753)
  AUTHORS   Cox,A.V.
  TITLE     Direct Submission
  JOURNAL   Submitted (19-AUG-1996) Cox A.V., Royal Botanic Gardens, Kew,
            Richmond, Surrey TW9 3AB, UK
FEATURES             Location/Qualifiers
     source          1..753
                     /organism="Cypripedium californicum"
                     /mol_type="genomic DNA"
                     /db_xref="taxon:53039"
     misc_feature    1..380
                     /note="internal transcribed spacer 1"
     gene            381..550
                     /gene="5.8S rRNA"
     rRNA            381..550
                     /gene="5.8S rRNA"
                     /product="5.8S ribosomal RNA"
     misc_feature    551..753
                     /note="internal transcribed spacer 2"
ORIGIN
        1 cgtaacaagg tttccgtagg tgaacctgcg gaaggatcat tgttgagaca acagaatata
       61 tgatcgagtg aatctggagg acctgtggta actcagctcg tcgtggcact gcttttgtcg
      121 tgaccctgct ttgttgttgg gcctcctcaa gagctttcat ggcaggtttg aactttagta
      181 cggtgcagtt tgcgccaagt catataaagc atcactgatg aatgacatta ttgtcagaaa
      241 aaatcagagg ggcagtatgc tactgagcat gccagtgaat ttttatgact ctcgcaacgg
      301 atatcttggc tctaacatcg atgaagaacg cagctaaatg cgataagtgg tgtgaattgc
      361 agaatcccgt gaaccatcga gtctttgaac gcaagttgcg ctcgaggcca tcaggctaag
      421 ggcacgcctg cctgggcgtc gtgtgttgcg tctctcctac caatgcttgc ttggcatatc
      481 gctaagctgg cattatacgg atgtgaatga ttggcccctt gtgcctaggt gcggtgggtc
      541 taaggattgt tgctttgatg ggtaggaatg tggcacgagg tggagaatgc taacagtcat
      601 aaggctgcta tttgaatccc ccatgttgtt gtattttttc gaacctacac aagaacctaa
      661 ttgaacccca atggagctaa aataaccatt gggcagttga tttccattca gatgcgaccc
      721 caggtcaggc ggggccaccc gctgagttga ggc
//
"""
    return io.BytesIO(gbk_str)
