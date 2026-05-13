"""
Realistic mock Indian district court judgments.
Covers 3 sections with deliberate inconsistencies planted for the consistency scorer.
"""

JUDGMENTS = [
    # ── Section 138 NI Act (Cheque Dishonour) ──────────────────────────────
    {
        "case_id": "CC_138_2019_MH_001",
        "court": "Judicial Magistrate First Class, Pune",
        "date": "2019-03-14",
        "judge": "Shri R.K. Deshmukh",
        "section_cited": "Section 138 NI Act",
        "outcome": "convicted",
        "state": "Maharashtra",
        "facts_summary": "Accused issued a cheque of Rs. 5,00,000 towards repayment of a hand loan. Cheque was dishonoured due to insufficient funds. Complainant issued statutory demand notice within 30 days. Accused failed to repay within 15 days of notice.",
        "legal_reasoning": "The complainant has established all ingredients of Section 138 NI Act beyond reasonable doubt. The cheque was issued for a legally enforceable debt. Dishonour is proved by bank memo. Notice was duly served. Non-payment within stipulated time is proved. Accused convicted and sentenced to imprisonment of 1 year and fine of Rs. 7,50,000.",
        "raw_text": "IN THE COURT OF JUDICIAL MAGISTRATE FIRST CLASS, PUNE. Case No. CC/138/2019. State v. Ramesh Patil. ORDER: The accused Ramesh Patil is convicted under Section 138 of the Negotiable Instruments Act, 1881 for dishonour of cheque bearing No. 004521 dated 10.01.2019 for Rs. 5,00,000 drawn on Bank of Maharashtra. The complainant Suresh Mehta has proved beyond reasonable doubt that the cheque was issued for a legally enforceable debt, was dishonoured due to insufficient funds, and the accused failed to pay the demanded amount within the statutory period. Sentenced to undergo Simple Imprisonment for one year and to pay fine of Rs. 7,50,000.",
        "citations": []
    },
    {
        "case_id": "CC_138_2020_MH_002",
        "court": "Judicial Magistrate First Class, Nashik",
        "date": "2020-07-22",
        "judge": "Smt. P.V. Kulkarni",
        "section_cited": "Section 138 NI Act",
        "outcome": "acquitted",
        "state": "Maharashtra",
        "facts_summary": "Accused issued a cheque of Rs. 4,80,000 towards repayment of a hand loan. Cheque was dishonoured due to insufficient funds. Complainant issued demand notice after 32 days of dishonour, exceeding the 30-day statutory window.",
        "legal_reasoning": "The notice issued by complainant is beyond the statutory period of 30 days prescribed under Section 138 NI Act. A demand notice issued after the limitation period is not a valid notice under the proviso to Section 138. The complaint is therefore not maintainable. Accused acquitted.",
        "raw_text": "IN THE COURT OF JUDICIAL MAGISTRATE FIRST CLASS, NASHIK. Case No. CC/245/2020. State v. Anil Sharma. ORDER: The accused Anil Sharma is acquitted of the offence under Section 138 NI Act. The demand notice was issued on the 32nd day from the date of dishonour, which falls outside the 30-day window prescribed under the proviso to Section 138. As notice is a jurisdictional requirement and the same is fatally defective, the complaint fails at the threshold. Accused acquitted.",
        "citations": []
    },
    {
        "case_id": "CC_138_2018_TN_003",
        "court": "Judicial Magistrate, Coimbatore",
        "date": "2018-11-05",
        "judge": "Thiru K. Ramasamy",
        "section_cited": "Section 138 NI Act",
        "outcome": "convicted",
        "state": "Tamil Nadu",
        "facts_summary": "Accused issued post-dated cheque of Rs. 12,00,000 as security for a business loan. Cheque dishonoured. Complainant issued notice within 30 days. Accused claimed cheque was issued as security and not for a legally enforceable debt.",
        "legal_reasoning": "The plea that the cheque was issued as security cannot be accepted as the accused himself admitted in cross-examination that there was an outstanding due. A cheque issued as security, when presented and dishonoured, attracts Section 138 NI Act if issued in discharge of a legally enforceable debt or liability. Relying on M/s Indus Airways v. Magnum Aviation, the accused is convicted.",
        "raw_text": "IN THE COURT OF JUDICIAL MAGISTRATE, COIMBATORE. Case No. CC/89/2018. STATE v. Gopalakrishnan. ORDER: The defence that the cheque was merely a security cheque cannot sustain in view of the accused's own admission. The Hon'ble Supreme Court has settled in M/s Indus Airways v. Magnum Aviation that a cheque issued as security for a debt, when presented and returned unpaid, attracts the rigours of Section 138 NI Act. Accused convicted.",
        "citations": ["CC_138_SC_2014_IND"]
    },
    {
        "case_id": "CC_138_SC_2014_IND",
        "court": "Supreme Court of India",
        "date": "2014-08-19",
        "judge": "Justice R.M. Lodha",
        "section_cited": "Section 138 NI Act",
        "outcome": "convicted",
        "state": "National",
        "facts_summary": "Landmark case establishing that cheques issued as security attract Section 138 NI Act if presented for discharge of a legally enforceable debt.",
        "legal_reasoning": "If a cheque is issued as security but represents a legally enforceable liability, its dishonour attracts Section 138. The court cannot permit accused to take shelter under the 'security cheque' defence when debt is otherwise proved.",
        "raw_text": "SUPREME COURT OF INDIA. M/s Indus Airways Pvt. Ltd. v. Magnum Aviation Pvt. Ltd. CIVIL APPEAL No. 5903/2014. HELD: A cheque issued as security for a debt constitutes a cheque in discharge of a legally enforceable liability within the meaning of Section 138 NI Act. The defence of 'security cheque' cannot be sustained when the debt itself is proved. Appeal dismissed.",
        "citations": []
    },
    {
        "case_id": "CC_138_2021_TN_004",
        "court": "Judicial Magistrate, Chennai",
        "date": "2021-02-18",
        "judge": "Tmt. S. Kavitha",
        "section_cited": "Section 138 NI Act",
        "outcome": "acquitted",
        "state": "Tamil Nadu",
        "facts_summary": "Accused issued cheque of Rs. 3,50,000 as repayment of a hand loan. Cheque dishonoured. Notice issued in time. Accused claimed cheque was stolen from his possession and he had not issued it voluntarily.",
        "legal_reasoning": "The accused has raised a plea of theft of cheque leaf. The handwriting expert's report raises reasonable doubt about the signature. The complainant has failed to rebut this doubt. In cases where the accused raises a defence which creates reasonable doubt, benefit of doubt must go to accused. Acquitted.",
        "raw_text": "IN THE COURT OF JUDICIAL MAGISTRATE, CHENNAI. Case No. CC/317/2021. The accused raised the plea that the cheque leaf in question was stolen from a cheque book that was reported missing in 2020. The handwriting expert examined has stated that there is a possibility of forgery. This creates reasonable doubt in the prosecution case which the complainant has failed to rebut. Accused is entitled to the benefit of doubt. Acquitted.",
        "citations": []
    },
    {
        "case_id": "CC_138_2022_KA_005",
        "court": "Civil Judge and JMFC, Bengaluru",
        "date": "2022-09-11",
        "judge": "Sri H.M. Venkatesh",
        "section_cited": "Section 138 NI Act",
        "outcome": "convicted",
        "state": "Karnataka",
        "facts_summary": "Accused issued cheque of Rs. 8,00,000 for repayment of business loan. Cheque dishonoured. Notice issued in time. Accused did not appear after bail and was tried ex-parte.",
        "legal_reasoning": "The accused having been duly served and having chosen not to appear, the court proceeds ex-parte. The complainant's evidence is uncontroverted. All ingredients of Section 138 proved. Accused convicted ex-parte.",
        "raw_text": "IN THE COURT OF CIVIL JUDGE AND JMFC, BENGALURU. The accused Vikram Singh having been duly served with summons failed to appear and was proceeded against ex-parte vide order dated 14.06.2022. The complainant's uncontroverted evidence establishes all the ingredients of Section 138 NI Act. Convicted and sentenced to pay fine of Rs. 16,00,000.",
        "citations": []
    },
    {
        "case_id": "CC_138_2020_RJ_006",
        "court": "Judicial Magistrate, Jaipur",
        "date": "2020-04-03",
        "judge": "Shri M.L. Meena",
        "section_cited": "Section 138 NI Act",
        "outcome": "acquitted",
        "state": "Rajasthan",
        "facts_summary": "Accused issued cheque of Rs. 6,00,000. Cheque dishonoured. Notice issued in time. Complainant could not produce original cheque in court — only a photocopy was exhibited.",
        "legal_reasoning": "The original cheque is the primary document in a Section 138 case. A photocopy of the cheque is not admissible as primary evidence under the Evidence Act without proof of loss of original. Complainant failed to lay foundation for secondary evidence. Acquitted for want of primary evidence.",
        "raw_text": "IN THE COURT OF JUDICIAL MAGISTRATE, JAIPUR. The complainant has exhibited only a photocopy of the cheque. No application under Section 65 of the Indian Evidence Act was made to admit secondary evidence. The original cheque is a sine qua non for conviction under Section 138 NI Act. In the absence of the original or proper secondary evidence, the complainant fails to prove the foundational fact. Accused acquitted.",
        "citations": []
    },

    # ── Section 420 IPC (Cheating) ─────────────────────────────────────────
    {
        "case_id": "SC_420_2019_DL_007",
        "court": "Sessions Court, New Delhi",
        "date": "2019-06-25",
        "judge": "Shri Arun Kumar Sharma",
        "section_cited": "Section 420 IPC",
        "outcome": "convicted",
        "state": "Delhi",
        "facts_summary": "Accused falsely represented himself as a government contractor with contracts worth crores and induced the complainant to invest Rs. 25,00,000 in a fictitious project. Money was never returned and the accused fled.",
        "legal_reasoning": "The ingredients of Section 420 IPC are fully established: (1) deceptive representation, (2) inducement to deliver property, (3) dishonest intention at the time of making the representation. The accused's conduct of fleeing after receiving money conclusively establishes mens rea. Convicted and sentenced to 3 years rigorous imprisonment.",
        "raw_text": "IN THE COURT OF SESSIONS, NEW DELHI. Sessions Case No. 44/2019. The prosecution has proved beyond reasonable doubt that the accused made false representations about being a government-empanelled contractor, induced the complainant to part with Rs. 25 lakhs, and absconded. The three ingredients of Section 420 IPC stand established. Convicted. Sentenced to 3 years RI and fine of Rs. 5,00,000.",
        "citations": []
    },
    {
        "case_id": "SC_420_2021_DL_008",
        "court": "Sessions Court, New Delhi",
        "date": "2021-11-30",
        "judge": "Smt. Rekha Verma",
        "section_cited": "Section 420 IPC",
        "outcome": "acquitted",
        "state": "Delhi",
        "facts_summary": "Accused promised complainant returns of 24% per annum on investment of Rs. 20,00,000 in a real estate scheme. Returns were not paid. Complainant filed case under Section 420 IPC.",
        "legal_reasoning": "For Section 420, dishonest intention must exist at the time of making the representation. A failed business venture or investment scheme does not by itself constitute cheating. The accused made genuine attempts to run the scheme before it failed due to market conditions. No mens rea at inception proved. Acquitted.",
        "raw_text": "IN THE COURT OF SESSIONS, NEW DELHI. Sessions Case No. 112/2021. A civil dispute dressed in criminal clothing cannot constitute Section 420 IPC. The complainant invested in a real estate scheme that failed. The prosecution has not established that the accused had fraudulent intent at the time of taking the investment. Business failure is not cheating. Acquitted.",
        "citations": []
    },
    {
        "case_id": "SC_420_2018_MH_009",
        "court": "Sessions Court, Mumbai",
        "date": "2018-08-14",
        "judge": "Shri D.W. Deshpande",
        "section_cited": "Section 420 IPC",
        "outcome": "convicted",
        "state": "Maharashtra",
        "facts_summary": "Accused collected advance payments from 47 complainants totaling Rs. 1.2 crore for supply of construction materials and disappeared after receiving money without supplying goods.",
        "legal_reasoning": "Where an accused collects money from multiple complainants, fails to supply goods, and deliberately evades, the pattern of conduct itself establishes mens rea under Section 420. Convicted on all counts.",
        "raw_text": "IN THE COURT OF SESSIONS, MUMBAI. The scale and pattern of the accused's conduct — collecting advances from 47 persons and disappearing — is sufficient to establish fraudulent intent at inception. This is not a case of mere breach of contract. Convicted under Section 420 IPC. Sentenced to 4 years RI and restitution of Rs. 1.2 crore.",
        "citations": ["SC_420_2019_DL_007"]
    },
    {
        "case_id": "SC_420_2022_TN_010",
        "court": "Sessions Court, Chennai",
        "date": "2022-03-07",
        "judge": "Tmt. V. Meenakshi",
        "section_cited": "Section 420 IPC",
        "outcome": "acquitted",
        "state": "Tamil Nadu",
        "facts_summary": "Accused took Rs. 18,00,000 from complainant promising a flat in a housing scheme. Flat not delivered due to builder's insolvency. Complainant filed Section 420 IPC.",
        "legal_reasoning": "The accused cannot be held criminally liable for the insolvency of a third-party builder. The accused was himself a victim of the builder's fraud. No dishonest intention at the time of inducement established. Civil remedy under RERA more appropriate. Acquitted.",
        "raw_text": "IN THE COURT OF SESSIONS, CHENNAI. The evidence on record shows that the accused was a sub-agent who collected money in good faith from the complainant and paid it to the builder. When the builder became insolvent, the scheme collapsed. Criminal liability under Section 420 IPC requires personal mens rea at the time of the transaction, which is absent here. Complainant advised to approach RERA. Acquitted.",
        "citations": []
    },

    # ── Section 304B IPC (Dowry Death) ────────────────────────────────────
    {
        "case_id": "SC_304B_2017_UP_011",
        "court": "Sessions Court, Lucknow",
        "date": "2017-12-19",
        "judge": "Shri S.N. Tripathi",
        "section_cited": "Section 304B IPC",
        "outcome": "convicted",
        "state": "Uttar Pradesh",
        "facts_summary": "Deceased wife died within 7 years of marriage due to burns. Evidence of persistent dowry demands by husband and in-laws established. Presumption under Section 113B Evidence Act invoked.",
        "legal_reasoning": "All ingredients of Section 304B are satisfied: death within 7 years of marriage, death due to burns, soon before death the deceased was subjected to cruelty in connection with dowry demand. Presumption under Section 113B Evidence Act is irrebuttable unless accused proves absence of demand. Convicted.",
        "raw_text": "IN THE COURT OF SESSIONS, LUCKNOW. Sessions Case No. 78/2017. The prosecution has established that the deceased Sunita Devi died of burn injuries within 3 years of marriage. The parents of the deceased have credibly deposed about persistent dowry demands. The statutory presumption under Section 113B of the Indian Evidence Act applies with full force. The accused have failed to rebut the presumption. Convicted under Section 304B IPC and sentenced to 7 years RI.",
        "citations": []
    },
    {
        "case_id": "SC_304B_2020_UP_012",
        "court": "Sessions Court, Agra",
        "date": "2020-09-08",
        "judge": "Smt. N.K. Agarwal",
        "section_cited": "Section 304B IPC",
        "outcome": "acquitted",
        "state": "Uttar Pradesh",
        "facts_summary": "Deceased wife died within 5 years of marriage in a road accident. Prosecution alleged that she had been forced out of the house due to dowry demands and was hence on road when the accident occurred.",
        "legal_reasoning": "Section 304B requires that death be caused 'otherwise than under normal circumstances' and that it be connected to dowry harassment. A road accident death, even if preceded by a domestic dispute, does not satisfy the nexus requirement unless there is evidence that the accused caused or abetted the death itself. Nexus not proved. Acquitted.",
        "raw_text": "IN THE COURT OF SESSIONS, AGRA. The death of the deceased in a road accident is a tragedy but it cannot be attributed to dowry harassment without a direct causal link. The prosecution has not established that the accused's conduct caused or materially contributed to the accident. The presumption under Section 113B Evidence Act does not apply where the cause of death is an independent intervening cause. Accused acquitted.",
        "citations": []
    },
    {
        "case_id": "SC_304B_2019_RJ_013",
        "court": "Sessions Court, Jodhpur",
        "date": "2019-05-21",
        "judge": "Shri P.K. Mathur",
        "section_cited": "Section 304B IPC",
        "outcome": "convicted",
        "state": "Rajasthan",
        "facts_summary": "Deceased found hanging within 2 years of marriage. Evidence of dowry demands and cruelty by husband's family established through multiple witnesses. Accused claimed it was suicide due to depression.",
        "legal_reasoning": "Even if the immediate cause of death is suicide, if the accused drove the deceased to suicide through sustained dowry-related cruelty, the offence of Section 304B is made out. The defence of depression cannot be accepted where there is credible evidence of dowry harassment. Convicted.",
        "raw_text": "IN THE COURT OF SESSIONS, JODHPUR. The law is well settled that dowry death includes cases where the accused's cruelty drove the deceased to suicide. The defence of depression is an afterthought not supported by any medical record prior to the incident. Five independent witnesses have corroborated the deceased's complaints about dowry demands. Convicted under Section 304B and sentenced to 10 years RI.",
        "citations": ["SC_304B_2017_UP_011"]
    },
    {
        "case_id": "SC_304B_2021_KA_014",
        "court": "Sessions Court, Mangaluru",
        "date": "2021-07-14",
        "judge": "Sri K.R. Bhat",
        "section_cited": "Section 304B IPC",
        "outcome": "acquitted",
        "state": "Karnataka",
        "facts_summary": "Deceased died of poisoning within 4 years of marriage. Family alleged dowry demands. However, deceased's own letters and diary entries indicated she had been suffering from severe clinical depression unrelated to marital issues.",
        "legal_reasoning": "Documentary evidence in the form of the deceased's personal diary and letters to a friend clearly indicate that her mental anguish was not connected to dowry harassment but to clinical depression predating the marriage. The presumption under Section 113B stands rebutted by this documentary evidence. Acquitted.",
        "raw_text": "IN THE COURT OF SESSIONS, MANGALURU. The deceased's personal diary, exhibited as Ex. P-14, contains detailed entries over 18 months describing severe depression predating her marriage. Her letters to her friend, Ex. P-17, make no mention of dowry demands and instead focus on her mental health struggles. This documentary evidence, being in the deceased's own hand, convincingly rebuts the presumption under Section 113B Evidence Act. Accused acquitted.",
        "citations": []
    },
    {
        "case_id": "SC_304B_HC_2016_IND",
        "court": "High Court of Delhi",
        "date": "2016-03-11",
        "judge": "Justice Pradeep Nandrajog",
        "section_cited": "Section 304B IPC",
        "outcome": "convicted",
        "state": "National",
        "facts_summary": "Landmark HC ruling: Dowry death includes cases where accused's sustained cruelty drives deceased to take own life. Suicide induced by dowry harassment is within the scope of Section 304B.",
        "legal_reasoning": "The legislature's intent in enacting Section 304B was to address all unnatural deaths of young wives connected to dowry. A restrictive interpretation that excludes suicide-as-dowry-death would defeat the legislative purpose. Cruelty-induced suicide within 7 years of marriage in connection with dowry is Section 304B.",
        "raw_text": "HIGH COURT OF DELHI. Crl. A. No. 234/2016. HELD: Section 304B IPC is not restricted to homicidal deaths. Where the prosecution establishes that the deceased took her own life as a direct result of sustained cruelty and harassment in connection with dowry demand, the requirements of Section 304B are satisfied. The object of the provision would be defeated by a narrow interpretation. Appeal allowed. Conviction restored.",
        "citations": []
    },

    # ── Additional 138 cases for richer consistency scoring ────────────────
    {
        "case_id": "CC_138_2023_MH_015",
        "court": "Judicial Magistrate First Class, Aurangabad",
        "date": "2023-01-30",
        "judge": "Shri A.B. Joshi",
        "section_cited": "Section 138 NI Act",
        "outcome": "convicted",
        "state": "Maharashtra",
        "facts_summary": "Accused issued cheque of Rs. 4,50,000 as repayment of hand loan. Dishonoured due to insufficient funds. Notice issued within 30 days. Accused denied knowledge of the cheque.",
        "legal_reasoning": "Once a cheque bearing the accused's signature is dishonoured, the presumption under Section 139 NI Act operates in favour of the complainant. The accused's bare denial is insufficient to rebut this statutory presumption. Convicted.",
        "raw_text": "IN THE COURT OF JMFC, AURANGABAD. Section 139 NI Act raises a presumption that the cheque was issued for a legally enforceable debt. This presumption can only be rebutted by cogent evidence, not a mere denial. The accused has not placed any credible evidence to rebut the presumption. Convicted and sentenced to fine of Rs. 9,00,000.",
        "citations": ["CC_138_SC_2014_IND"]
    },
    {
        "case_id": "CC_138_2023_TN_016",
        "court": "Judicial Magistrate, Madurai",
        "date": "2023-06-14",
        "judge": "Thiru P. Arumugam",
        "section_cited": "Section 138 NI Act",
        "outcome": "acquitted",
        "state": "Tamil Nadu",
        "facts_summary": "Accused issued cheque of Rs. 5,20,000. Dishonoured. Notice issued in time. Accused claimed the loan was already repaid in cash before cheque was presented and produced a signed receipt.",
        "legal_reasoning": "The accused has produced a signed receipt for repayment predating the presentment of the cheque. The complainant could not satisfactorily explain the existence of the receipt. The statutory presumption stands rebutted. Acquitted.",
        "raw_text": "IN THE COURT OF JUDICIAL MAGISTRATE, MADURAI. The accused has rebutted the presumption under Section 139 NI Act by producing a signed repayment receipt dated prior to the presentment of the cheque. The complainant's cross-examination was not satisfactory on this point. Reasonable doubt created. Accused acquitted.",
        "citations": []
    },
]

CITATION_GRAPH = {
    "CC_138_2019_MH_001": [],
    "CC_138_2020_MH_002": [],
    "CC_138_2018_TN_003": ["CC_138_SC_2014_IND"],
    "CC_138_SC_2014_IND": [],
    "CC_138_2021_TN_004": [],
    "CC_138_2022_KA_005": [],
    "CC_138_2020_RJ_006": [],
    "SC_420_2019_DL_007": [],
    "SC_420_2021_DL_008": [],
    "SC_420_2018_MH_009": ["SC_420_2019_DL_007"],
    "SC_420_2022_TN_010": [],
    "SC_304B_2017_UP_011": [],
    "SC_304B_2020_UP_012": [],
    "SC_304B_2019_RJ_013": ["SC_304B_2017_UP_011", "SC_304B_HC_2016_IND"],
    "SC_304B_2021_KA_014": [],
    "SC_304B_HC_2016_IND": [],
    "CC_138_2023_MH_015": ["CC_138_SC_2014_IND"],
    "CC_138_2023_TN_016": [],
}
