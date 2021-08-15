DISCOVERY_SERVICE_V1_DISCOVERY_DOC = {
    "basePath": "/discovery/v1/",
    "baseUrl": "https://www.googleapis.com/discovery/v1/",
    "batchPath": "batch/discovery/v1",
    "description": "Provides information about other Google APIs, such as what APIs are available, the resource, and method details for each API.",
    "discoveryVersion": "v1",
    "documentationLink": "https://developers.google.com/discovery/",
    "etag": '"J3WqvAcMk4eQjJXvfSI4Yr8VouA/kUro_lCKdlL_SgLaWY4jaDKtqsk"',
    "icons": {
        "x16": "http://www.google.com/images/icons/feature/filing_cabinet_search-g16.png",
        "x32": "http://www.google.com/images/icons/feature/filing_cabinet_search-g32.png",
    },
    "id": "discovery:v1",
    "kind": "discovery#restDescription",
    "name": "discovery",
    "ownerDomain": "google.com",
    "ownerName": "Google",
    "parameters": {
        "alt": {
            "default": "json",
            "description": "Data format for the response.",
            "enum": ["json"],
            "enumDescriptions": ["Responses with Content-Type of application/json"],
            "location": "query",
            "type": "string",
        },
        "fields": {
            "description": "Selector specifying which fields to include in a partial response.",
            "location": "query",
            "type": "string",
        },
        "key": {
            "description": "API key. Your API key identifies your project and provides you with API access, quota, and reports. Required unless you provide an OAuth 2.0 token.",
            "location": "query",
            "type": "string",
        },
        "oauth_token": {
            "description": "OAuth 2.0 token for the current user.",
            "location": "query",
            "type": "string",
        },
        "prettyPrint": {
            "default": "true",
            "description": "Returns response with indentations and line breaks.",
            "location": "query",
            "type": "boolean",
        },
        "quotaUser": {
            "description": "An opaque string that represents a user for quota purposes. Must not exceed 40 characters.",
            "location": "query",
            "type": "string",
        },
        "userIp": {
            "description": "Deprecated. Please use quotaUser instead.",
            "location": "query",
            "type": "string",
        },
    },
    "protocol": "rest",
    "resources": {
        "apis": {
            "methods": {
                "getRest": {
                    "description": "Retrieve the description of a particular version of an api.",
                    "httpMethod": "GET",
                    "id": "discovery.apis.getRest",
                    "parameterOrder": ["api", "version"],
                    "parameters": {
                        "api": {
                            "description": "The name of the API.",
                            "location": "path",
                            "required": True,
                            "type": "string",
                        },
                        "version": {
                            "description": "The version of the API.",
                            "location": "path",
                            "required": True,
                            "type": "string",
                        },
                    },
                    "path": "apis/{api}/{version}/rest",
                    "response": {"$ref": "RestDescription"},
                },
                "list": {
                    "description": "Retrieve the list of APIs supported at this endpoint.",
                    "httpMethod": "GET",
                    "id": "discovery.apis.list",
                    "parameters": {
                        "name": {
                            "description": "Only include APIs with the given name.",
                            "location": "query",
                            "type": "string",
                        },
                        "preferred": {
                            "default": "false",
                            "description": "Return only the preferred version of an API.",
                            "location": "query",
                            "type": "boolean",
                        },
                    },
                    "path": "apis",
                    "response": {"$ref": "DirectoryList"},
                },
            }
        }
    },
    "revision": "20181107",
    "rootUrl": "https://www.googleapis.com/",
    "schemas": {
        "DirectoryList": {
            "id": "DirectoryList",
            "properties": {
                "discoveryVersion": {
                    "default": "v1",
                    "description": "Indicate the version of the Discovery API used to generate this doc.",
                    "type": "string",
                },
                "items": {
                    "description": "The individual directory entries. One entry per api/version pair.",
                    "items": {
                        "properties": {
                            "description": {
                                "description": "The description of this API.",
                                "type": "string",
                            },
                            "discoveryLink": {
                                "description": "A link to the discovery document.",
                                "type": "string",
                            },
                            "discoveryRestUrl": {
                                "description": "The URL for the discovery REST document.",
                                "type": "string",
                            },
                            "documentationLink": {
                                "description": "A link to human readable documentation for the API.",
                                "type": "string",
                            },
                            "icons": {
                                "description": "Links to 16x16 and 32x32 icons representing the API.",
                                "properties": {
                                    "x16": {
                                        "description": "The URL of the 16x16 icon.",
                                        "type": "string",
                                    },
                                    "x32": {
                                        "description": "The URL of the 32x32 icon.",
                                        "type": "string",
                                    },
                                },
                                "type": "object",
                            },
                            "id": {
                                "description": "The id of this API.",
                                "type": "string",
                            },
                            "kind": {
                                "default": "discovery#directoryItem",
                                "description": "The kind for this response.",
                                "type": "string",
                            },
                            "labels": {
                                "description": "Labels for the status of this API, such as labs or deprecated.",
                                "items": {"type": "string"},
                                "type": "array",
                            },
                            "name": {
                                "description": "The name of the API.",
                                "type": "string",
                            },
                            "preferred": {
                                "description": "True if this version is the preferred version to use.",
                                "type": "boolean",
                            },
                            "title": {
                                "description": "The title of this API.",
                                "type": "string",
                            },
                            "version": {
                                "description": "The version of the API.",
                                "type": "string",
                            },
                        },
                        "type": "object",
                    },
                    "type": "array",
                },
                "kind": {
                    "default": "discovery#directoryList",
                    "description": "The kind for this response.",
                    "type": "string",
                },
            },
            "type": "object",
        },
        "JsonSchema": {
            "id": "JsonSchema",
            "properties": {
                "$ref": {
                    "description": 'A reference to another schema. The value of this property is the "id" of another schema.',
                    "type": "string",
                },
                "additionalProperties": {
                    "$ref": "JsonSchema",
                    "description": "If this is a schema for an object, this property is the schema for any additional properties with dynamic keys on "
                    "this object.",
                },
                "annotations": {
                    "description": "Additional information about this property.",
                    "properties": {
                        "required": {
                            "description": "A list of methods for which this property is required on requests.",
                            "items": {"type": "string"},
                            "type": "array",
                        }
                    },
                    "type": "object",
                },
                "default": {
                    "description": "The default value of this property (if one exists).",
                    "type": "string",
                },
                "description": {
                    "description": "A description of this object.",
                    "type": "string",
                },
                "enum": {
                    "description": "Values this parameter may take (if it is an enum).",
                    "items": {"type": "string"},
                    "type": "array",
                },
                "enumDescriptions": {
                    "description": 'The descriptions for the enums. Each position maps to the corresponding value in the "enum" array.',
                    "items": {"type": "string"},
                    "type": "array",
                },
                "format": {
                    "description": "An additional regular expression or key that helps constrain the value. For more details see: "
                    "http://tools.ietf.org/html/draft-zyp-json-schema-03#section-5.23",
                    "type": "string",
                },
                "id": {
                    "description": "Unique identifier for this schema.",
                    "type": "string",
                },
                "items": {
                    "$ref": "JsonSchema",
                    "description": "If this is a schema for an array, this property is the schema for each element in the array.",
                },
                "location": {
                    "description": "Whether this parameter goes in the query or the path for REST requests.",
                    "type": "string",
                },
                "maximum": {
                    "description": "The maximum value of this parameter.",
                    "type": "string",
                },
                "minimum": {
                    "description": "The minimum value of this parameter.",
                    "type": "string",
                },
                "pattern": {
                    "description": "The regular expression this parameter must conform to. Uses Java 6 regex format: "
                    "http://docs.oracle.com/javase/6/docs/api/java/util/regex/Pattern.html",
                    "type": "string",
                },
                "properties": {
                    "additionalProperties": {
                        "$ref": "JsonSchema",
                        "description": "A single property of this object. The value is itself a JSON Schema object describing this "
                        "property.",
                    },
                    "description": "If this is a schema for an object, list the schema for each property of this object.",
                    "type": "object",
                },
                "readOnly": {
                    "description": "The value is read-only, generated by the service. The value cannot be modified by the client. If the value is included in a "
                    "POST, PUT, or PATCH request, it is ignored by the service.",
                    "type": "boolean",
                },
                "repeated": {
                    "description": "Whether this parameter may appear multiple times.",
                    "type": "boolean",
                },
                "required": {
                    "description": "Whether the parameter is required.",
                    "type": "boolean",
                },
                "type": {
                    "description": "The value type for this schema. A list of values can be found here: "
                    "http://tools.ietf.org/html/draft-zyp-json-schema-03#section-5.1",
                    "type": "string",
                },
                "variant": {
                    "description": "In a variant data type, the value of one property is used to determine how to interpret the entire entity. Its value must exist "
                    "in a map of descriminant values to schema names.",
                    "properties": {
                        "discriminant": {
                            "description": "The name of the type discriminant property.",
                            "type": "string",
                        },
                        "map": {
                            "description": "The map of discriminant value to schema to use for parsing..",
                            "items": {
                                "properties": {
                                    "$ref": {"type": "string"},
                                    "type_value": {"type": "string"},
                                },
                                "type": "object",
                            },
                            "type": "array",
                        },
                    },
                    "type": "object",
                },
            },
            "type": "object",
        },
        "RestDescription": {
            "id": "RestDescription",
            "properties": {
                "auth": {
                    "description": "Authentication information.",
                    "properties": {
                        "oauth2": {
                            "description": "OAuth 2.0 authentication information.",
                            "properties": {
                                "scopes": {
                                    "additionalProperties": {
                                        "description": "The scope value.",
                                        "properties": {
                                            "description": {
                                                "description": "Description of "
                                                "scope.",
                                                "type": "string",
                                            }
                                        },
                                        "type": "object",
                                    },
                                    "description": "Available OAuth 2.0 scopes.",
                                    "type": "object",
                                }
                            },
                            "type": "object",
                        }
                    },
                    "type": "object",
                },
                "basePath": {
                    "description": "[DEPRECATED] The base path for REST requests.",
                    "type": "string",
                },
                "baseUrl": {
                    "description": "[DEPRECATED] The base URL for REST requests.",
                    "type": "string",
                },
                "batchPath": {
                    "description": "The path for REST batch requests.",
                    "type": "string",
                },
                "canonicalName": {
                    "description": "Indicates how the API name should be capitalized and split into various parts. Useful for generating pretty class "
                    "names.",
                    "type": "string",
                },
                "description": {
                    "description": "The description of this API.",
                    "type": "string",
                },
                "discoveryVersion": {
                    "default": "v1",
                    "description": "Indicate the version of the Discovery API used to generate this doc.",
                    "type": "string",
                },
                "documentationLink": {
                    "description": "A link to human readable documentation for the API.",
                    "type": "string",
                },
                "etag": {
                    "description": "The ETag for this response.",
                    "readOnly": True,
                    "type": "string",
                },
                "exponentialBackoffDefault": {
                    "description": "Enable exponential backoff for suitable methods in the generated clients.",
                    "type": "boolean",
                },
                "features": {
                    "description": "A list of supported features for this API.",
                    "items": {"type": "string"},
                    "type": "array",
                },
                "icons": {
                    "description": "Links to 16x16 and 32x32 icons representing the API.",
                    "properties": {
                        "x16": {
                            "description": "The URL of the 16x16 icon.",
                            "type": "string",
                        },
                        "x32": {
                            "description": "The URL of the 32x32 icon.",
                            "type": "string",
                        },
                    },
                    "type": "object",
                },
                "id": {"description": "The ID of this API.", "type": "string"},
                "kind": {
                    "default": "discovery#restDescription",
                    "description": "The kind for this response.",
                    "type": "string",
                },
                "labels": {
                    "description": "Labels for the status of this API, such as labs or deprecated.",
                    "items": {"type": "string"},
                    "type": "array",
                },
                "methods": {
                    "additionalProperties": {
                        "$ref": "RestMethod",
                        "description": "An individual method description.",
                    },
                    "description": "API-level methods for this API.",
                    "type": "object",
                },
                "name": {"description": "The name of this API.", "type": "string"},
                "ownerDomain": {
                    "description": "The domain of the owner of this API. Together with the ownerName and a packagePath values, this can be used to "
                    "generate a library for this API which would have a unique fully qualified name.",
                    "type": "string",
                },
                "ownerName": {
                    "description": "The name of the owner of this API. See ownerDomain.",
                    "type": "string",
                },
                "packagePath": {
                    "description": "The package of the owner of this API. See ownerDomain.",
                    "type": "string",
                },
                "parameters": {
                    "additionalProperties": {
                        "$ref": "JsonSchema",
                        "description": "Description of a single parameter.",
                    },
                    "description": "Common parameters that apply across all apis.",
                    "type": "object",
                },
                "protocol": {
                    "default": "rest",
                    "description": "The protocol described by this document.",
                    "type": "string",
                },
                "resources": {
                    "additionalProperties": {
                        "$ref": "RestResource",
                        "description": "An individual resource description. Contains methods and sub-resources related to this "
                        "resource.",
                    },
                    "description": "The resources in this API.",
                    "type": "object",
                },
                "revision": {
                    "description": "The version of this API.",
                    "type": "string",
                },
                "rootUrl": {
                    "description": "The root URL under which all API services live.",
                    "type": "string",
                },
                "schemas": {
                    "additionalProperties": {
                        "$ref": "JsonSchema",
                        "description": "An individual schema description.",
                    },
                    "description": "The schemas for this API.",
                    "type": "object",
                },
                "servicePath": {
                    "description": "The base path for all REST requests.",
                    "type": "string",
                },
                "title": {"description": "The title of this API.", "type": "string"},
                "version": {
                    "description": "The version of this API.",
                    "type": "string",
                },
                "version_module": {"type": "boolean"},
            },
            "type": "object",
        },
        "RestMethod": {
            "id": "RestMethod",
            "properties": {
                "description": {
                    "description": "Description of this method.",
                    "type": "string",
                },
                "etagRequired": {
                    "description": "Whether this method requires an ETag to be specified. The ETag is sent as an HTTP If-Match or If-None-Match header.",
                    "type": "boolean",
                },
                "httpMethod": {
                    "description": "HTTP method used by this method.",
                    "type": "string",
                },
                "id": {
                    "description": "A unique ID for this method. This property can be used to match methods between different versions of Discovery.",
                    "type": "string",
                },
                "mediaUpload": {
                    "description": "Media upload parameters.",
                    "properties": {
                        "accept": {
                            "description": "MIME Media Ranges for acceptable media uploads to this method.",
                            "items": {"type": "string"},
                            "type": "array",
                        },
                        "maxSize": {
                            "description": 'Maximum size of a media upload, such as "1MB", "2GB" or "3TB".',
                            "type": "string",
                        },
                        "protocols": {
                            "description": "Supported upload protocols.",
                            "properties": {
                                "resumable": {
                                    "description": "Supports the Resumable Media Upload protocol.",
                                    "properties": {
                                        "multipart": {
                                            "default": "true",
                                            "description": "True if this endpoint supports "
                                            "uploading multipart media.",
                                            "type": "boolean",
                                        },
                                        "path": {
                                            "description": "The URI path to be used for upload. "
                                            "Should be used in conjunction with the "
                                            "basePath property at the api-level.",
                                            "type": "string",
                                        },
                                    },
                                    "type": "object",
                                },
                                "simple": {
                                    "description": "Supports uploading as a single HTTP request.",
                                    "properties": {
                                        "multipart": {
                                            "default": "true",
                                            "description": "True if this endpoint supports upload "
                                            "multipart media.",
                                            "type": "boolean",
                                        },
                                        "path": {
                                            "description": "The URI path to be used for upload. Should "
                                            "be used in conjunction with the basePath "
                                            "property at the api-level.",
                                            "type": "string",
                                        },
                                    },
                                    "type": "object",
                                },
                            },
                            "type": "object",
                        },
                    },
                    "type": "object",
                },
                "parameterOrder": {
                    "description": "Ordered list of required parameters, serves as a hint to clients on how to structure their method signatures. The array "
                    'is ordered such that the "most-significant" parameter appears first.',
                    "items": {"type": "string"},
                    "type": "array",
                },
                "parameters": {
                    "additionalProperties": {
                        "$ref": "JsonSchema",
                        "description": "Details for a single parameter in this method.",
                    },
                    "description": "Details for all parameters in this method.",
                    "type": "object",
                },
                "path": {
                    "description": "The URI path of this REST method. Should be used in conjunction with the basePath property at the api-level.",
                    "type": "string",
                },
                "request": {
                    "description": "The schema for the request.",
                    "properties": {
                        "$ref": {
                            "description": "Schema ID for the request schema.",
                            "type": "string",
                        },
                        "parameterName": {
                            "description": "parameter name.",
                            "type": "string",
                        },
                    },
                    "type": "object",
                },
                "response": {
                    "description": "The schema for the response.",
                    "properties": {
                        "$ref": {
                            "description": "Schema ID for the response schema.",
                            "type": "string",
                        }
                    },
                    "type": "object",
                },
                "scopes": {
                    "description": "OAuth 2.0 scopes applicable to this method.",
                    "items": {"type": "string"},
                    "type": "array",
                },
                "supportsMediaDownload": {
                    "description": "Whether this method supports media downloads.",
                    "type": "boolean",
                },
                "supportsMediaUpload": {
                    "description": "Whether this method supports media uploads.",
                    "type": "boolean",
                },
                "supportsSubscription": {
                    "description": "Whether this method supports subscriptions.",
                    "type": "boolean",
                },
                "useMediaDownloadService": {
                    "description": 'Indicates that downloads from this method should use the download service URL (i.e. "/download"). Only applies '
                    "if the method supports media download.",
                    "type": "boolean",
                },
            },
            "type": "object",
        },
        "RestResource": {
            "id": "RestResource",
            "properties": {
                "methods": {
                    "additionalProperties": {
                        "$ref": "RestMethod",
                        "description": "Description for any methods on this resource.",
                    },
                    "description": "Methods on this resource.",
                    "type": "object",
                },
                "resources": {
                    "additionalProperties": {
                        "$ref": "RestResource",
                        "description": "Description for any sub-resources on this resource.",
                    },
                    "description": "Sub-resources on this resource.",
                    "type": "object",
                },
            },
            "type": "object",
        },
    },
    "servicePath": "discovery/v1/",
    "title": "APIs Discovery Service",
    "version": "v1",
}
