chembox_part_1 ="""
{{Chembox
| ImageFile = <!-- svg.svg -->
| ImageFile_Ref	= 
| ImageAlt = 
| ImageSize = <!-- 244 (any number) -->
| IUPACName = %s
| OtherNames = {{Unbulleted list
  | %s
  }}
""".lstrip('\n')
chembox_part_2 = """
| Section1={{Chembox Identifiers
| index_label =  <!-- name -->
| CASNo = %s
| CASNo_Ref = 
| ChemSpiderID = %s
| ChemSpiderID_Ref = 
| ChEBI = %s
| ChEMBL = %s
| EC_number = %s
| EC_number_Comment = 
| StdInChI = %s
| StdInChIKey = %s 
| SMILES = %s
| PubChem = %s
| UNII = %s
| UNII_Ref = 
 }}
""".lstrip('\n')
chembox_part_3 ="""
|Section2={{Chembox Properties
| %s 
 }}
}}

'''%s''' is

== See also ==
* [[]]

== References ==
{{Reflist}}

[[Category:Indole alkaloids]]

{{Alkaloid-stub}}
""".lstrip('\n')

chembox_template = """iupac, other_1\ncas_no, chemspider, chebi, chembl, ec_no, inchi, inchi_key, smiles, pubchem_cid, unii\nformula, title\n"""
