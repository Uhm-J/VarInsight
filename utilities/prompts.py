from langchain import PromptTemplate

REPORT_TEMPLATE = """
The nucleotide change c.1026_1027delinsCA is expected to result in the amino acid substitution p.(Gly343Ser) in the SCN1A protein. A highly conserved amino acid is being altered, and the chemical difference between Gly and Ser is small (Grantham score: 56 [0-215]).
This variant has not been previously described in the literature and has not been found in approximately 250,000 reference alleles in the Genome Aggregation Database (gnomAD; http://gnomad.broadinstitute.org). The variant is listed once in the ClinVar database as likely pathogenic (class 4) without additional information about the patient's clinical presentation (https://www.ncbi.nlm.nih.gov/clinvar/RCV000497813/).
Pathogenic variants in the SCN1A gene are associated with various autosomal dominant conditions such as "generalized epilepsy with febrile seizures plus, type 2" (MIM 604403), Dravet syndrome (MIM 607208), "developmental and epileptic encephalopathy 6B, non-Dravet" (MIM 619317), and "familial hemiplegic migraine 3" (MIM 609634). Other changes involving the same amino acid (p.Gly343Arg, p.Gly343Cys, and p.Gly343Asp) have been described in the literature in patients with Dravet syndrome (Ishii et al. 2017 PMID: 28012175 and Brunklaus et al. 2020 PMID: 32090326).
"""

REPORT_CHAIN_PROMPT = f"""
If someone asks you to generate a report on a genetic variant, you will use the following template:

Question: "Write a report for the following variant: c.1026_1027delinsCA in SCN1A."

The following steps will be taken to generate the report:
1. You will extract the variant from the input text and search for it in the ClinVar database.
2. If the variant is found in ClinVar, you will use the information from ClinVar to generate the report.
3. You will search for the same protein changes in the gene and see if these variants are different from the input cdna variant.
4. Finally search for supporting literature on the variant and add it to the report.

{REPORT_TEMPLATE}

""" + """
That is the format, begin!
Question {QUESTION}
"""

REPORT_PROMPT = PromptTemplate(
    input_variables=["QUESTION"],
    template=REPORT_CHAIN_PROMPT
)