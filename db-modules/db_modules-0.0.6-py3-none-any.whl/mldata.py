class LoadAdaptedMLData:
    #Self connection if True 
    def __init__(self, connect):
        if connect == True: 
            self.connect()

    #Kaavyas code - connects to server 
    def connect(self):
        self.conn = psycopg2.connect(database= database,
                        user = user,
                        password = password,
                         host = host)
        self.curr = self.conn.cursor()
        print("Opened database successfully")
    
    #Prints out tables from the schema 
    def get_table_information(self):
        sql = 'SELECT * FROM information_schema.tables'
        self.curr.execute(sql)
        for row in self.curr: 
            print(row)
    
    #Lod annot objects
    def get_annot_objects(self, data):
        annotTypes = ["active_site","cdd","chebi","ec","gene3d","go_keywords","go_long",
                        "hamap","interpro","ko","npb","odbdesc","odbid","panther","pfam",
                        "pirsf","prints","prosite","reaction","signal_peptide","similarity",
                        "smart","subcellular_location","subunit","supfam","symbol","taxid",
                        "tigrfams","tm_region"]

        topLevel = ["description","embedding","sequence"]

        annotTypeJSON = {}
        for a in annotTypes: #Creating empty dict with keys from annotTypes
            annotTypeJSON[a] = {}

        topLevelJSON = {}
        annot_data = data['annot_results']
        for protein in annot_data:
            #print(annot_data[protein].keys())
            idx = annot_data[protein]["index"]
            id = annot_data[protein]["id"]
            for a in annotTypes:
                temp = {}
                temp["index"] = idx
                temp["id"] = id
                temp[a] = annot_data[protein][a]
                annotTypeJSON[a][protein] = temp

            temp = {}
            temp["index"] = idx
            temp["id"] = id
            for t in topLevel:
                temp[t] = annot_data[protein][t]

            topLevelJSON[protein] = temp

        annotTypeJSON["top_level"] = topLevelJSON

        annotTypeJSON['cluster_report'] = data['cluster_report']
        annotTypeJSON['hcslices'] = data['hcslices']
        annotTypeJSON['hcclusters'] = data['hcclusters']
        annotTypeJSON['proj2d'] = data['proj2d']
        annotTypeJSON['params'] = data['params']
        run_time = data["run_time"] #The variable run_time is being set to the value of the key run_time in data dict 
        status_code = data["status_code"] 
        annotation_id = data["annotation_id"]
        
        return annotTypeJSON
    
    #Gets run/annot id 
    def insert_adapated_data(self, annotTypeJSON,run_name, run_file,run_time,status_code,annotation_id, description):
        self.curr.execute('INSERT INTO run(run_name, run_file, description) VALUES(%s, %s, %s) RETURNING run_id;',(run_name,run_file, description))
        rid = 0
        for row in self.curr: rid = row[0]

        self.conn.commit()
        self.curr.execute("INSERT INTO annot_data(run_time, status_code, annotation_id) VALUES({},{},'{}') RETURNING annot_id;".format(run_time,status_code, annotation_id))
        annot_id = 0
        for row in self.curr: annot_id = row[0]
        self.conn.commit()

        for a in annotTypeJSON:

            s = str(json.dumps(annotTypeJSON[a]))
            sub_text = re.sub(pattern="'", string=s, repl="\'\'")
            sub_text = "[" + sub_text + "]"
            self.curr.execute("UPDATE annot_data SET {} = '{}' WHERE  annot_id = {};".format(a,json.dumps(sub_text),annot_id))

        self.conn.commit()

        self.curr.execute("UPDATE annot_data SET run_id = '{}'::uuid WHERE annot_id = {};".format(rid,annot_id))
        self.conn.commit()
        self.conn.close()