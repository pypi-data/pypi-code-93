"""AnaClient is a python module for accessing Rendered.AI's Ana Platform API."""
from anatools.api import AnaAPI
import os 
import pprint

class AnaClient:

    def __init__(self, workspaceId=None, environment='prod', verbose=False, email=None, password=None, local=False):
        import pyrebase, getpass, time, base64, json, traceback
        import anatools.envs as envs
        self.verbose = verbose
        if environment not in ['dev','test','prod','infra']: 
            print('Invalid environment argument, must be \'infra\', \'dev\', \'test\' or \'prod\'.')
            return None
        self.__environment = environment
        encodedbytes = envs.envs.encode('ascii')
        decodedbytes = base64.b64decode(encodedbytes)
        decodedenvs = json.loads(decodedbytes.decode('ascii'))
        envdata = decodedenvs[environment]
        self.__firebase = pyrebase.initialize_app(envdata)
        self.__url = envdata['graphURL']
        self.__auth = self.__firebase.auth()
        self.__timer = int(time.time())
        self.email = email
        self.__password = password
        self.__channels = None
        self.__pp = pprint.PrettyPrinter()
        loggedin = False
        if not self.email:
            print(f'Enter your credentials for the {envdata["name"]}.') 
            self.email = input('Email: ')
        if not self.__password:
            failcount = 1
            while not loggedin:
                self.__password = getpass.getpass()
                try:
                    self.__user = self.__auth.sign_in_with_email_and_password(self.email, self.__password)
                    loggedin = True
                except:
                    if failcount < 5:
                        print('\rInvalid password, please enter your password again.')
                        failcount += 1
                    else:
                        print(f'\rInvalid password, consider resetting your password at {envdata["website"]}/forgot-password.')
                        return
        if not loggedin:
            try:
                self.__user = self.__auth.sign_in_with_email_and_password(self.email, self.__password)
                loggedin = True
            except:
                if self.verbose == 'debug': traceback.print_exc()
                print(f'Failed to login to {envdata["name"]} with email ({email}).')
                return
  
        self.__uid = self.__user['localId']
        self.__headers = {'uid':self.__uid, 'idtoken':self.__user['idToken']}
        self.__logout = False
        if self.verbose == 'debug': 
            print(self.__uid)
            print(self.__user['idToken'])
        if local:
            os.environ['NO_PROXY'] = '127.0.0.1'
            self.__url = 'http://127.0.0.1:3000'
            print("Local is set to",self.__url)
        self.ana_api = AnaAPI(self.__url, self.__headers, self.verbose)

        self.__workspaces = self.get_workspaces()
        self.__organizations = self.get_organizations()
        if workspaceId:     
            self.__workspace = workspaceId
            if self.__workspace in self.__workspaces:
                self.__organization = self.__workspaces[self.__workspace]['organizationId']
        else:
            if len(self.__workspaces):
                self.__workspace = self.__workspaces[0]['workspaceId']
                self.__organization = self.__workspaces[0]['organizationId']
            else:
                self.__workspace = None
                self.__organization = self.__organizations[0]['organizationId']
        self.__channels = self.get_channels()

        if verbose: print(f'Signed into {envdata["name"]} with {self.email}, using workspace {self.__workspace}.')
        print(f'These are your organizations:')
        self.__pp.pprint(self.__organizations)
        print(f'The current organization is: {self.__organization}')



    def __refresh_token(self):
        import time
        if int(time.time())-self.__timer > int(self.__user['expiresIn']):
            self.__user = self.__auth.sign_in_with_email_and_password(self.email, self.__password)
            self.__headers = {'uid':self.__uid, 'idtoken':self.__user['idToken']}
            self.__timer = int(time.time())


    def __check_logout(self):
        if self.__logout:
            print('You are currently logged out, login to access the Ana tool.')
            return True
        self.__refresh_token()
        return False


    def logout(self, clear=False):
        """Logs out of the ana sdk and removes credentials from ana.
        """
        if self.__check_logout(): return
        self.email = None
        self.__logout = True
        del self.__password, self.__firebase, self.__url, self.__auth, self.__user, self.__uid, self.__headers, self.__workspace, self.__channels
    

    def login(self, workspace=None, environment='prod', email=None, password=None):
        """Log in to ana sdk 

        Parameters
        ----------
        workspace : str
            ID of the workspace to log in to. Uses default if not specified.
        environment : str
            Environment to log into. Defaults to production.

        """
        self.__init__(workspace, environment, self.verbose, email, password)
        return

    def get_organizations(self):
        """Shows the organizations the user belongs to and the user's role in that organization.

        Returns
        -------
        list
            List of members emails that belong to a workspace. 

        """  
        if self.__check_logout(): return
        return self.ana_api.getOrganizations()

    def edit_organization(self, name, organizationId=None):
        """Update the organization name. Uses current organization if no organizationId provided.

        Parameters
        ----------
        name : str
            Name to update organization to.
        organizationId : str
            Organization Id to update.


        Returns
        -------
        Bool
            True if organization was edited successfully, False otherwise.

        """  
        if self.__check_logout(): return
        if name is None: return
        if organizationId is None: organizationId = self.__organization
        return self.ana_api.editOrganization(organizationId, name)

    def create_organization(self, name):
        """Creates a new organization with provided name.

        Parameters
        ----------
        name : str
            Name of organization to create.

        Returns
        -------
        Bool
            True if organization was created successfully, False otherwise.

        """  
        if self.__check_logout(): return
        return self.ana_api.createOrganization(name)

    
    def delete_organization(self, organizationId):
        """Deletes an organization.

        Parameters
        ----------
        organizationId : str
            Id of organization to create.

        Returns
        -------
        Bool
            True if organization was deleted successfully, False otherwise.

        """  
        if self.__check_logout(): return
        return self.ana_api.deleteOrganization(organizationId)
        
    
    def get_workspace(self):
        """Get workspace id of current workspace. 

        Returns
        -------
        str
            Workspace ID of current workspace.

        """
        if self.__check_logout(): return
        return self.__workspace


    def set_workspace(self, workspaceId=None):
        """Set the workspace to the one you wish to work in.

        Parameters
        ----------
        workspaceid : str
            Workspace ID for the workspace you wish to work in. Uses default workspace if this is not set.

        """
        import requests
        if self.__check_logout(): return
        if workspaceId is None: return
        self.__workspace = workspaceId
        return self.__workspace
    
    def create_workspace(self, name, channels):
        """Create a new workspace with specific channels.

        Parameters
        ----------
        name : str    
            New workspace name.
        channels : list
            List of channel names to add to workspace. 

        Returns
        -------
        str
            Workspace ID if creation was successful. Otherwise returns message.

        """    
        import requests
        if self.__check_logout(): return
        if name is None: name = self.__uid
        channelIds = [self.__channels[channel] for channel in channels]
        return self.ana_api.createWorkspace(organizationId=self.__organization, name=name, channelIds = channelIds)


    def delete_workspace(self, workspaceId=None, prompt=True):
        """Delete an existing workspace. 

        Parameters
        ----------
        workspaceId : str    
            Workspace ID for workspace to get deleted. Deletes current workspace if not specified. 
        prompt: bool
            Set to True if avoiding prompts for deleting workspace.

        Returns
        -------
        str
            Success or failure message if workspace was sucessfully removed.

        """   
        import requests
        if self.__check_logout(): return
        if workspaceId is None: workspaceId = self.__workspace 
        if prompt:
            response = input('This will remove any configurations, graphs and datasets associated with this workspace.\nAre you certain you want to delete this workspace? (y/n)  ')
            if response not in ['Y', 'y', 'Yes', 'yes']: return
        return self.ana_api.deleteWorkspace(workspaceId=workspaceId)


    def edit_workspace(self, name, workspaceId=None, channels=None):
        """Edit workspace information. Provided channels list will result in the workspace having those channels. If channels is not provided, then no change will occur. 

        Parameters
        ----------
        name : str    
            New name to replace old one.
        workspaceId : str    
            Workspace ID for workspace to update.
        channels: list
            Names of channels to add to workspace.

        Returns
        -------
        str
            Success or failure message if workspace description was sucessfully updated.

        """  
        import requests
        if self.__check_logout(): return
        if name is None: return
        if workspaceId is None: workspaceId = self.__workspace
        if channels is None:    channelIds = None
        else:                   channelIds = [self.__channels[channel] for channel in channels]
        return self.ana_api.editWorkspace(workspaceId=workspaceId, name=name, channelIds=channelIds)
    
    
    def get_workspaces(self, organizationId=None, workspaceId=None):
        """Shows list of workspaces with id, name, and owner data.

        Returns
        -------
        dict
            Workspace data for all workspaces for a user.

        """  
        import requests
        if self.__check_logout(): return
        return self.ana_api.getWorkspaces(organizationId, workspaceId)
        

    def get_members(self, organizationId=None, workspaceId=None):
        """Get users of an organization optionally filtered on workspace.

        Parameters
        ----------
        organizationId : str
            Organization ID. Defaults to current if not specified.
        workspaceId : str
            Workspace Id. Optional.

        Returns
        -------
        json
            json object with users of an organization

        """
        if self.__check_logout(): return
        if organizationId is None: organizationId = self.__organization
        return self.ana_api.getMembers(organizationId=organizationId, workspaceId=workspaceId)

    def add_member(self, email, role=None, organizationId=None, workspaceId=None):
        """Add a user to an existing organization.

        Parameters
        ----------
        email: str
            Email of user to add.
        role : str
            Role for user. 
        organizationId : str
            Organization ID to add members too. Uses current if not specified.
        workspaceId : str    
            Workspace ID to add members to. Uses current if not specified.

        Returns
        -------
        str
            Response status if user got added to workspace succesfully. 

        """
        if self.__check_logout(): return
        if email is None: return
        return self.ana_api.addMember(email=email, role=role, organizationId=organizationId, workspaceId=workspaceId)


    def remove_member(self, email, organizationId=None, workspaceId=None):
        """Remove a member from an existing workspace.

        Parameters
        ----------
        email : str
            Member email to remove.
        organizationId: str
            Organization ID to remove member from. Removes from current organization if not specified.
        workspaceId : str    
            Workspace ID to remove member from. Removes from current workspace if not specified. 

        Returns
        -------
        str
            Response status if member got removed from organization or workspace succesfully. 

        """
        if self.__check_logout(): return
        return self.ana_api.removeMember(email=email, organizationId=organizationId, workspaceId=workspaceId)

    def edit_member(self, email, role, organizationId=None):
        """Edit a member's role. 

        Parameters
        ----------
        email : str
            Member email to edit.
        role: str
            Role to assign. 
        organizationId: str
            Organization ID to remove member from. Edits member in current organization if not specified.
        
        Returns
        -------
        str
            Response if member got edited succesfully. 

        """
        if self.__check_logout(): return
        if organizationId is None: organizationId = self.__organization
        return self.ana_api.editMember(email=email, role=role, organizationId=organizationId)


    def get_channels(self, organizationId=None, workspaceId=None, channelId=None):
        """Shows all channels available to the user. Can filter by organizationId, workspaceId, or channelId.

        Parameters
        ----------
        organizationId : str
            Filter channel list on what's available to the organization.
        workspaceId : str    
            Filter channel list on what's available to the workspace.
        channelId: str
            Filter channel list on the specific channelId.

        Returns
        -------
        list
            List of all possible channel names.

        """
        if self.__check_logout(): return
        if organizationId or workspaceId or channelId:
            return self.ana_api.getChannels(organizationId=organizationId, workspaceId=workspaceId, channelId=channelId)
        else:
            channels = {}
            resp = self.ana_api.getChannels(organizationId=organizationId, workspaceId=workspaceId, channelId=channelId)
            for channel in resp:
                channels[channel['name']] = channel['channelId']
            return channels

    
    def get_graphs(self, graphId=None, name=None, email=None, workspaceId=None):
        """Queries the workspace graphs based off provided parameters. Checks on graphId, name, or owner in this respective order within the specified workspace.
        If only workspace ID is provided, this will return all the graphs in a workspace. 

        Parameters
        ----------
        graphid : str
            GraphID to filter on. Optional.
        name : str
            Name of the graph to filter on. Optional.
        email: str
            Owner of graphs to filter on. Optional.
        workspaceId : str    
            Workspace ID to filter on. If none is provided, the default workspace will get used. 
        
        Returns
        -------
        list
            A list of graphs based off provided query parameters if any parameters match.

        """
        if self.__check_logout(): return
        if graphId is None: graphid = ''
        if name is None: name = ''
        if email is None: email = ''
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.getGraphs(workspaceId=workspaceId, graphId=graphId, name=name, email=email)


    def get_default_graph(self, channel):
        """Gets the default graph for a channel.

        Parameters
        ----------
        channel:
            Name of channel to get the default graph for.
       
        Returns
        -------
        json
            json data representing the graph.

        """
        if self.__check_logout(): return
        return self.ana_api.getDefaultGraph(channel=channel)


    def create_graph(self, name, channel, graph, description=None, workspaceId=None):
        """Generates a new graph based off provided parameters. 

        Parameters
        ----------
        name : str
            Graph name that will get generated.
        channel: str
            Name of channel to generate the graph with.
        graph: json
            Location of yaml file. Check out the readme for more details (step 3 for how to use ana)
        description: str
            Description of graph. Optional.
        workspaceId : str    
            Workspace ID create the graph in. If none is provided, the default workspace will get used. 

        
        Returns
        -------
        str
            The graph id if it was created sucessfully or an error message.

        """
        if self.__check_logout(): return
        if name is None or graph is None or channel is None: return
        if workspaceId is None: workspaceId = self.__workspace
        channelId = self.__channels[channel]
        return self.ana_api.createGraph(workspaceId=workspaceId, channelId=channelId, graph=graph, name=name, description=description)

    
    def edit_graph(self, graphId, description=None, name=None, workspaceId=None):
        """Update graph description and name. 

        Parameters
        ----------
        graphId : str
            Graph id to update.
        description: str
            New description to update.
        name: str
            New name to update.
        workspaceId : str    
            Workspace ID of the graph's workspace. If none is provided, the current workspace will get used. 
        
        Returns
        -------
        str
            A success or error message based on graph's update.

        """
        if self.__check_logout(): return
        if graphId is None: return
        if name is None and description is None: return
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.editGraph(workspaceId=workspaceId, graphId=graphId, name=name, description=description)

    def delete_graph(self, graphId, workspaceId=None):
        """Delete a graph in a workspace.

        Parameters
        ----------
        graphId : str
            Graph id to delete.
        workspaceId : str    
            Workspace ID of the graph's workspace. If none is provided, the current workspace will get used. 
        
        Returns
        -------
        str
            A success or error message based on graph's delete.

        """
        if self.__check_logout(): return
        if graphId is None: return
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.deleteGraph(workspaceId=workspaceId, graphId=graphId)
        

    def download_graph(self, graphId, workspaceId=None):
        """Download a graph.

        Parameters
        ----------
        graphId : str
            Graph ID of the graph to download.
        workspaceId : str    
            Workspace ID of the graph's workspace. If none is provided, the default workspace will get used. 
        
        Returns
        -------
        str
            A download URL that can be used in the browser or a failure message.

        """
        if self.__check_logout(): return
        if graphId is None: return
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.downloadGraph(workspaceId=workspaceId, graphId=graphId)

    
    def get_datasets(self, datasetId=None, name=None, email=None, workspaceId=None):
        """Queries the workspace datasets based off provided parameters. Checks on datasetId, name, owner in this respective order within the specified workspace.
        If only workspace ID is provided, this will return all the graphs in a workspace. 

        Parameters
        ----------
        datasetId : str
            Dataset ID to filter.
        name : str 
            Dataset name.   
        email: str
            Owner of the dataset.
        workspaceId : str
            Workspace ID of the graph's workspace. If none is provided, the current workspace will get used. 


        Returns
        -------
        str
            Information about the dataset based off the query parameters provided or a failure message. 

        """
        if self.__check_logout(): return
        if datasetId is None: datasetId = ''
        if name is None: name = ''
        if email is None: owner = ''
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.getDatasets(workspaceId=workspaceId, datasetId=datasetId, name=name, email=email)


    def create_dataset(self, name, graphId, description, interpretations=1, priority=1, seed=1, workspaceId=None):
        """Create a new dataset based off an existing graph. This will start a new job.

        Parameters
        ----------
        name: str
            Name for dataset. 
        graphId : str
            Graph ID of the graph to create dataset from.
        description : str 
            Description for new dataset.
        interpretations : int
            Number of interpretations.
        priority : int
            Job priority.
        seed : int
            Seed number.
        workspaceId : str
            Workspace ID of the graph's workspace. If none is provided, the current workspace will get used. 


        Returns
        -------
        str
            Success or failure message about dataset creation.

        """
        if self.__check_logout(): return
        if name is None or graphId is None: return
        if description is None: description = ''
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.createDataset(workspaceId=workspaceId, graphId=graphId, name=name, 
                    description=description, interpretations=interpretations, seed=seed, priority=priority)

    
    def edit_dataset(self, datasetId, description=None, name=None, workspaceId=None):
        """Update dataset description.

        Parameters
        ----------
        datasetId : str
            Dataset ID to update description for.
        description : str 
            New description.
        name: str
            New name for dataset.
        workspaceId : str
            Workspace ID of the dataset to get updated. If none is provided, the current workspace will get used. 


        Returns
        -------
        str
            Success or failure message about dataset update.

        """
        if self.__check_logout(): return
        if datasetId is None: return
        if workspaceId is None: workspaceId = self.__workspace
        if name is None and description is None: return
        return self.ana_api.editDataset(workspaceId=workspaceId, datasetId=datasetId, name=name, description=description)
        
    def delete_dataset(self, datasetId, workspaceId=None):
        """Delete an existing dataset.

        Parameters
        ----------
        datasetId : str
            Dataset ID of dataset to delete.
        workspaceId : str
            Workspace ID that the dataset is in. If none is provided, the current workspace will get used. 


        Returns
        -------
        str
            Success or failure message about dataset deletion.

        """
        if self.__check_logout(): return
        if datasetId is None: return
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.deleteDataset(workspaceId=workspaceId, datasetId=datasetId)
        

    def download_dataset(self, datasetId, workspaceId=None):
        """Download a dataset.

        Parameters
        ----------
        datasetId : str
            Dataset ID of dataset to download.
        workspaceId : str
            Workspace ID that the dataset is in. If none is provided, the default workspace will get used. 


        Returns
        -------
        str
            Success or failure message about dataset download.

        """
        import requests
        if self.__check_logout(): return
        if datasetId is None: datasetId
        if workspaceId is None: workspaceId = self.__workspace
        url = self.ana_api.downloadDataset(workspaceId=workspaceId, datasetId=datasetId)        
        fname = url.split('?')[0].split('/')[-1]
        downloadresponse = requests.get(url=url)
        with open(fname, 'wb') as outfile:
            outfile.write(downloadresponse.content)
        del downloadresponse
        return fname


    def register_docker(self, channel):
        """Register the docker image of a channel.

        Parameters
        ----------
        channel : str
            Channel name for the docker image, this must match the channel docker image.
        
        Returns
        -------
        str
            Success or failure message about docker registration.

        """
        import requests, docker, base64, json, time
        import anatools.envs as envs
        if self.__environment != 'dev': 
            print('Docker containers can only be registered in the Development environment.')
            return False
        if self.__check_logout(): return
        if channel is None: return False
        encodedbytes = envs.envs.encode('ascii')
        decodedbytes = base64.b64decode(encodedbytes)
        decodedenvs = json.loads(decodedbytes.decode('ascii'))
        envdata = decodedenvs[self.__environment]
        
        # check if channel image is in docker
        dockerclient = docker.from_env()
        try: channelimage = dockerclient.images.get(channel)
        except docker.errors.ImageNotFound:
            print('Could not find Docker image with name {channel}.')
            return False
        except:
            print('Error connecting to Docker.')
            return False
        
        # get ecr password
        encodedpass = self.ana_api.registerDocker(self.__channels[channel])
        if encodedpass:
            encodedbytes = encodedpass.encode('ascii')
            decodedbytes = base64.b64decode(encodedbytes)
            decodedpass = decodedbytes.decode('ascii').split(':')[-1]
        else: 
            print('Failed to retrieve Docker credentials.')
            return

        # tag and push image
        print(f"Pushing {channel} Docker Image. This could take awhile...", end='')
        time.sleep(1)
        reponame = envdata['ecrURL'].replace('https://','')+'/'+channel
        resp = channelimage.tag(reponame)
        if self.verbose == 'debug': print( dockerclient.images.push(reponame, auth_config={'username':'AWS', 'password':decodedpass}) )
        else: resp = dockerclient.images.push(reponame, auth_config={'username':'AWS', 'password':decodedpass})
        print("Complete!")

        # confirm image pushed / start registration
        response = self.ana_api.registerChannel(self.__channels[channel])
        if not response: print('Failed to confirm Docker upload.')

        # cleanup docker
        resp = dockerclient.images.remove(reponame)
        return response


    def register_package_data(self,package,location):
        """Upload a folder to be available for use with a channel. This is used when uploading multiple files. 

        Parameters
        ----------
        package : str
            Folder name of the package inside the location parameter.
        location : str
            Local directory to search in for the package. It is the path to the package folder.
        
        Returns
        -------
        str
            Succes or error message about package upload.

        """
        # blocked 
        # https://bitbucket.org/renderedai/infra/src/main/infrastructure/graphql/resolvers/services/registerPackageData.ts
        # location = path to packages
        # package = example
        # rename to register_package_data
        # use box.blend and check if it copied to s3. clean up other files except box.blend 
        # Create "example", verify box.blend copied into it. Try a bigger file (1G) to fiugre out copy limit, provide internet speed 
        # result of test: Error with response and upload did not happen
        
        import requests, os, json

        if package not in os.listdir(location):
            print(f"Incorrect location of package: {os.listdir(location)}")
            return
        fileroot = os.path.abspath(os.path.join(location,package))

        uploadfiles = []

        for root, dirs, files in os.walk(fileroot):
            for upfile in files:
                uploadfiles.append(os.path.join(root,upfile))
        
        numfiles = len(uploadfiles)
        getkey = None
        presignedurl = None
        #TODO add more outputs to check graphql works and if presigned url process works
        for i,filepath in enumerate(uploadfiles):
            filename = filepath.split('/')[-1]
            print(f'Uploading file {i} of {numfiles}:    {filename}', end='/r')
            key = filepath.replace(fileroot,'').replace(filename,'')
            if getkey != key:
                getkey = key
                presignedurl = self.ana_api.registerData(package=package, key=key)
                
            if presignedurl:
                with open(filepath, 'rb') as data:
                    files = {'file': (filepath, data)}
                    print(files)
                    response = requests.post(presignedurl, data=presignedurl['fields'], files=files)
                    if response.status_code != 204: 
                        print('Upload failed.')
                        return
                print('Upload complete!')    


    def register_datafile(self,package,filepath):
        """Upload single data file to be available for use with a channel.

        Parameters
        ----------
        package : str
            File name.
        filepath : str
            Local directory to search in for the filename. It is the path to the filename.
        
        Returns
        -------
        str
            Succes or error message about file upload.

        """
        import requests, os
        key = filepath.split(f'/packages/{package}/')[-1]
        filename = key.split('/')[-1]
        key = key.replace(filename,'')
        presignedurl = self.ana_api.registerData(package=package, key=key)
        
        if presignedurl:
            with open(filepath, 'rb') as data:
                files = {'file': (filename, data)}
                response = requests.post(presignedurl['url'], data=presignedurl['fields'], files=files)
                if response.status_code != 204: 
                    print('Upload failed.')
                    return
            print('Upload complete!') 


    def create_channel(self, name, dataVolumes=None, instanceType=None, organizationId=None, timeout=None):
        """Create a new channel.

        Parameters
        ----------
        name : str
            Name of new channel.
        dataVolumes : str or list
            Data Volume name(s) in AWS to use data files from. This is the package that was registered.
        instanceType: str
            The EC2 instance the channel runs on (ie. p2.xlarge)
        organizationId: str
            Organization Id for which this channel must belong to. Will create the channel in the current organization if organization Id is not provided. 
        Returns
        -------
        str
            Succes or error message about channel creation.

        """
        if name is None: 
            print('Must provide channel name.')
            return
        if dataVolumes is None: dataVolumes = []
        if instanceType is None: instanceType = 'p2.xlarge'
        if organizationId is None: organizationId = self.__organization
        if timeout is None: timeout = 5
        return self.ana_api.createManagedChannel(organizationId, name, dataVolumes=dataVolumes, instanceType=instanceType, timeout=timeout)
        

    def deploy_channel(self, channel, environment='test'):
        """Deploy a channel between environments.

        Parameters
        ----------
        channel : str
            Name of channel to deploy.
        environment : str
            Environment to deploy channel to. Defaults to test environment.

        Returns
        -------
        str
            Succes or error message about channel deployment.

        """
        return self.ana_api.deployChannel(self.__channels[channel], environment=environment)
        

    def create_annotation(self, datasetId, format, map, workspaceId=None):
        """Generate an image annotation for an existing dataset.

        Parameters
        ----------
        datasetId : str
            Dataset ID to generate annotation for.
        format : str
            Image annotation format. Currently only COCO is supported.
        map: str
            Image annotation mapping. Currently only afv is supported.
        workspaceId: str
            Workspace ID of the dataset to generate annotation for. If none is provided, the current workspace will get used. 

        Returns
        -------
        str
            Succes or error message about generating the annotation.

        """
        import json
        if self.__check_logout(): return
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.createAnnotation(workspaceId=workspaceId, datasetId=datasetId, format=format, map=map)
        

    def download_annotation(self, datasetId, annotationId, workspaceId=None):
        """Download a generated image annotation file.

        Parameters
        ----------
        datasetId : str
            Dataset ID to download image annotation for.
        annotationId : str
            Id of previously generated image annotation. 
        workspaceId: str
            Workspace ID of the dataset to generate annotation for. If none is provided, the current workspace will get used. 

        Returns
        -------
        str
            URL if annotation download was successful or failure message. The URL can be used within a browser to download the image annotation file.

        """
        if self.__check_logout(): return
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.downloadAnnotation(workspaceId=workspaceId, datasetId=datasetId, annotationId=annotationId)


    def cancel_dataset(self, datasetId, workspaceId=None):
        """Stop a running job.

        Parameters
        ----------
        datasetId : str
            Dataset ID of the running job to stop.
        workspaceId: str
            Workspace ID of the running job. If none is provided, the default workspace will get used. 

        Returns
        -------
        str
            Succes or error message about stopping the job execution.

        """
        if self.__check_logout(): return
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.cancelDataset(workspaceId=workspaceId, datasetId=datasetId)


    def get_organization_usage(self, organizationId, year, month, workspaceId=None, member=None):
        """Get organization usage optionally filtered on workspace or a user. 

        Parameters
        ----------
        organizationId : str
            Organization ID. Defaults to current if not specified.
        year: str
            Usage year to filter on.
        month: str
            Usage month to filter on.
        workspaceId : str
            Workspace Id. Optional.
        member: str
            User email. Optional.

        Returns
        -------
        json
            json object with organization usage by channels, instanceType, and time as integer.

        """
        if self.__check_logout(): return
        if organizationId is None: organizationId = self.__organization
        return self.ana_api.getOrganizationUsage(organizationId=organizationId, year=year, month=month, workspaceId=workspaceId, member=member)


    def get_managed_channels(self, organizationId=None, channel=None):
        """Get managed channels by organization.

        Parameters
        ----------
        organizationId : str
            Organization ID. Defaults to current if not specified.
        channel : name
            Channel name to filter.
       
        Returns
        -------
        json
            channel data

        """
        if self.__check_logout(): return
        if organizationId is None: organizationId = self.__organization
        channelId = None
        if channel: channelId = self.__channels[channel]
        return self.ana_api.getManagedChannels(organizationId=organizationId, channelId=channelId)


    def create_managed_channel(self, name, organizationId=None, dataVolumes=None, instanceType=None, timeout=None):
        """Create a managed channel for your organization.

        Parameters
        ----------
        organizationId : str
            Organization ID. Defaults to current if not specified.
        name : name
            Channel name.
        dataVolumes : str
            Data volume
        instanceType: str
            AWS Instance type
        timeout: int
            Timeout
       
        Returns
        -------
        json
            channel data

        """
        if self.__check_logout(): return
        if organizationId is None: organizationId = self.__organization
        return self.ana_api.createManagedChannel(organizationId=organizationId, name=name, dataVolumes=dataVolumes, instanceType=instanceType, timeout=timeout)


    def get_platform_limits(self, tier=None, setting=None):
        """Get information about Platform limits and setting.

        Parameters
        ----------
        tier : str
            Tier
        setting : str
            Setting name.
       
        Returns
        -------
        json
            Platform limit information.

        """
        if self.__check_logout(): return
        return self.ana_api.getPlatformLimits(tier=tier, setting=setting)


    def set_platform_limit(self, tier, setting, limit):
        """Set Platform limits for a tier and a setting.

        Parameters
        ----------
        tier : str
            Tier
        setting : str
            Setting name.
        limit: int
            Limit to set.
       
        Returns
        -------
        json
            Platform limit information.

        """
        if self.__check_logout(): return
        return self.ana_api.setPlatformLimit(tier=tier, setting=setting, limit=limit)


    def get_organization_limits(self, organizationId=None, setting=None):
        """Get information about Organization limits and setting.

        Parameters
        ----------
        organizationId : str
            Organization ID. Defaults to current if not specified.
        setting : str
            Setting name.
        
        Returns
        -------
        json
            Organization limit information.

        """
        if self.__check_logout(): return
        if organizationId is None: organizationId = self.__organization
        return self.ana_api.getOrganizationLimits(organizationId=organizationId, setting=setting)


    def set_organization_limit(self, setting, limit, organizationId=None):
        """Set Organization limits for a setting.

        Parameters
        ----------
        organizationId : str
            Organization ID. Defaults to current if not specified.
        setting : str
            Setting name.
        limit: int
            Limit to set at.
        
        Returns
        -------
        json
            Organization limit information.

        """
        if self.__check_logout(): return
        if organizationId is None: organizationId = self.__organization
        return self.ana_api.setOrganizationLimit(organizationId=organizationId, setting=setting, limit=limit)


    def get_workspace_limits(self, workspaceId=None, setting=None):
        """Get information about Organization limits and setting.

        Parameters
        ----------
        workspaceId : str
            Workspace ID. Defaults to current if not specified.
        setting : str
            Setting name.
        
        Returns
        -------
        json
            Workspace limit information.

        """
        if self.__check_logout(): return
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.getWorkspaceLimits(workspaceId=workspaceId, setting=setting)


    def set_workspace_limit(self, setting, limit, workspaceId=None):
        """Get information about Organization limits and setting.

        Parameters
        ----------
        workspaceId : str
            Workspace ID. Defaults to current if not specified.
        setting : str
            Setting name.
        limit : Int
            Limit to set at.
        
        Returns
        -------
        json
            Workspace limit information.

        """
        if self.__check_logout(): return
        if workspaceId is None: workspaceId = self.__workspace
        return self.ana_api.setWorkspaceLimit(workspaceId=workspaceId, setting=setting, limit=limit)


    def add_channel_access(self, channelId, organizationId=None):
        """Add access to a channel for an organization.

        Parameters
        ----------
        channel : str
            Name of channel to add access for.
        organizationId : str
            Organization ID. Defaults to current if not specified.
        
        Returns
        -------
        json
            Access status. 

        """
        if self.__check_logout(): return
        if organizationId is None: organizationId = self.__organization
        return self.ana_api.addChannelOrganization(channelId=channelId, organizationId=organizationId)


    def remove_channel_access(self, channelId, organizationId=None):
        """Remove access to a channel for an organization.

        Parameters
        ----------
        channel : str
            Name of channel to remove access to.
        organizationId : str
            Organization ID. Defaults to current if not specified.
        
        Returns
        -------
        json
            Access status. 

        """
        if self.__check_logout(): return
        if organizationId is None: organizationId = self.__organization
        return self.ana_api.removeChannelOrganization(channelId=channelId, organizationId=organizationId)
