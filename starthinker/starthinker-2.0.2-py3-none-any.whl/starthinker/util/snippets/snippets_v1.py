URI = """{
 "auth": {
  "oauth2": {
   "scopes": {
    "https://www.googleapis.com/auth/userinfo.email": {
     "description": "View your email address"
    }
   }
  }
 },
 "basePath": "/_ah/api/snippets/v1/",
 "baseUrl": "https://snippets-hrdb.googleplex.com/_ah/api/snippets/v1/",
 "batchPath": "batch",
 "description": "Snippets API Library",
 "discoveryVersion": "v1",
 "icons": {
  "x16": "https://www.gstatic.com/images/branding/product/1x/googleg_16dp.png",
  "x32": "https://www.gstatic.com/images/branding/product/1x/googleg_32dp.png"
 },
 "id": "snippets:v1",
 "kind": "discovery#restDescription",
 "methods": {
  "listByConstraints": {
   "httpMethod": "GET",
   "id": "snippets.listByConstraints",
   "parameters": {
    "startDate": {
     "location": "query",
     "type": "string"
    },
    "endDate": {
     "location": "query",
     "type": "string"
    },
    "startWeekNumber": {
     "format": "int32",
     "location": "query",
     "type": "integer"
    },
    "endWeekNumber": {
     "format": "int32",
     "location": "query",
     "type": "integer"
    },
    "quarterNumber": {
     "format": "int32",
     "location": "query",
     "type": "integer"
    },
    "yearNumber": {
     "format": "int32",
     "location": "query",
     "type": "integer"
    },
    "userGroupKey": {
     "location": "query",
     "type": "string"
    },
    "includeDrafts": {
     "location": "query",
     "type": "boolean"
    }
   },
   "path": "snippets",
   "response": {
    "$ref": "SnippetEntityCollection"
   },
   "scopes": [
    "https://www.googleapis.com/auth/snippets",
    "https://www.googleapis.com/auth/snippets.readonly"
   ]
  }
 },
 "name": "snippets",
 "parameters": {
  "alt": {
   "default": "json",
   "description": "Data format for the response.",
   "enum": [
    "json"
   ],
   "enumDescriptions": [
    "Responses with Content-Type of application/json"
   ],
   "location": "query",
   "type": "string"
  },
  "fields": {
   "description": "Selector specifying which fields to include in a partial response.",
   "location": "query",
   "type": "string"
  },
  "key": {
   "description": "API key. Your API key identifies your project and provides you with API access, quota, and reports. Required unless you provide an OAuth 2.0 token.",
   "location": "query",
   "type": "string"
  },
  "oauth_token": {
   "description": "OAuth 2.0 token for the current user.",
   "location": "query",
   "type": "string"
  },
  "prettyPrint": {
   "default": "true",
   "description": "Returns response with indentations and line breaks.",
   "location": "query",
   "type": "boolean"
  },
  "quotaUser": {
   "description": "Available to use for quota purposes for server-side applications. Can be any arbitrary string assigned to a user, but should not exceed 40 characters. Overrides userIp if both are provided.",
   "location": "query",
   "type": "string"
  },
  "userIp": {
   "description": "IP address of the site where the request originates. Use this if you want to enforce per-user limits.",
   "location": "query",
   "type": "string"
  }
 },
 "protocol": "rest",
 "rootUrl": "https://snippets-hrdb.googleplex.com/_ah/api/",
 "schemas": {
  "Key": {
   "id": "Key",
   "properties": {
    "appId": {
     "type": "string"
    },
    "complete": {
     "type": "boolean"
    },
    "id": {
     "format": "int64",
     "type": "string"
    },
    "kind": {
     "type": "string"
    },
    "name": {
     "type": "string"
    },
    "namespace": {
     "type": "string"
    },
    "parent": {
     "$ref": "Key"
    }
   },
   "type": "object"
  },
  "SnippetEntity": {
   "id": "SnippetEntity",
   "properties": {
    "deleted": {
     "type": "boolean"
    },
    "draft": {
     "type": "boolean"
    },
    "key": {
     "$ref": "Key"
    },
    "keyNameOrId": {
     "type": "string"
    },
    "markdown": {
     "type": "boolean"
    },
    "modifiedDate": {
     "format": "date-time",
     "type": "string"
    },
    "personId": {
     "format": "int64",
     "type": "string"
    },
    "quarter": {
     "format": "int32",
     "type": "integer"
    },
    "submitDate": {
     "format": "date-time",
     "type": "string"
    },
    "text": {
     "$ref": "Text"
    },
    "textFromString": {
     "type": "string"
    },
    "visibility": {
     "type": "string"
    },
    "weekNumber": {
     "format": "int32",
     "type": "integer"
    },
    "year": {
     "format": "int32",
     "type": "integer"
    }
   },
   "type": "object"
  },
  "SnippetEntityCollection": {
   "id": "SnippetEntityCollection",
   "properties": {
    "items": {
     "items": {
      "$ref": "SnippetEntity"
     },
     "type": "array"
    }
   },
   "type": "object"
  },
  "Text": {
   "id": "Text",
   "properties": {
    "value": {
     "type": "string"
    }
   },
   "type": "object"
  }
 },
 "servicePath": "snippets/v1/",
 "version": "v1"
}
"""
