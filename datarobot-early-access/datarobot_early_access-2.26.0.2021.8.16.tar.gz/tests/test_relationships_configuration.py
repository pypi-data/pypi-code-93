import responses

from datarobot import RelationshipsConfiguration


@responses.activate
def test_relationships_config_creation(
    relationships_configuration, create_dataset_definitions, create_relationships
):
    responses.add(
        responses.POST,
        "https://host_name.com/relationshipsConfigurations/",
        json=relationships_configuration,
    )

    relationships_configuration = RelationshipsConfiguration.create(
        dataset_definitions=create_dataset_definitions, relationships=create_relationships,
    )
    assert responses.calls[0].request.method == "POST"
    assert relationships_configuration.id == "5a530498d5c1f302d6d176c8"
    assert len(relationships_configuration.dataset_definitions) == 2
    assert len(relationships_configuration.relationships) == 2


@responses.activate
def test_relationships_config_retrieve(
    relationships_configuration, create_dataset_definitions, create_relationships
):
    id = relationships_configuration["id"]
    responses.add(
        responses.GET,
        "https://host_name.com/relationshipsConfigurations/{}/".format(id),
        json=relationships_configuration,
    )

    result = RelationshipsConfiguration(id=id).get()

    assert responses.calls[0].request.method == "GET"
    assert result.id == id
    assert len(result.dataset_definitions) == 2
    assert len(result.relationships) == 2
    for actual, expected in zip(result.dataset_definitions, create_dataset_definitions):
        assert actual["identifier"] == expected["identifier"]
        assert actual["catalog_version_id"] == expected["catalogVersionId"]
        assert actual["catalog_id"] == expected["catalogId"]
        assert actual["snapshot_policy"] == expected["snapshotPolicy"]

    actual = result.relationships[1]
    expected = create_relationships[1]
    assert actual["dataset1_identifier"] == expected["dataset1Identifier"]
    assert actual["dataset2_identifier"] == expected["dataset2Identifier"]
    assert actual["dataset1_keys"] == expected["dataset1Keys"]
    assert actual["dataset2_keys"] == expected["dataset2Keys"]
    assert actual["feature_derivation_window_end"] == expected["featureDerivationWindowEnd"]
    assert actual["feature_derivation_window_start"] == expected["featureDerivationWindowStart"]
    assert (
        actual["feature_derivation_window_time_unit"] == expected["featureDerivationWindowTimeUnit"]
    )
    assert actual["prediction_point_rounding"] == expected["predictionPointRounding"]
    assert (
        actual["prediction_point_rounding_time_unit"] == expected["predictionPointRoundingTimeUnit"]
    )


@responses.activate
def test_relationships_config_replace(
    relationships_configuration, create_dataset_definitions, create_relationships
):
    responses.add(
        responses.PUT,
        "https://host_name.com/relationshipsConfigurations/R-ID/",
        json=relationships_configuration,
    )

    relationships_configuration = RelationshipsConfiguration("R-ID").replace(
        dataset_definitions=create_dataset_definitions, relationships=create_relationships,
    )
    assert responses.calls[0].request.method == "PUT"
    assert relationships_configuration.id == "5a530498d5c1f302d6d176c8"
    assert len(relationships_configuration.dataset_definitions) == 2
    assert len(relationships_configuration.relationships) == 2


@responses.activate
def test_relationships_config_delete(relationships_configuration):
    id = relationships_configuration["id"]
    url = "https://host_name.com/relationshipsConfigurations/{}/".format(id)
    responses.add(responses.DELETE, url)

    relationships_config = RelationshipsConfiguration(id=id)
    relationships_config.delete()

    assert responses.calls[0].request.method == responses.DELETE
    assert responses.calls[0].request.url == url


@responses.activate
def test_jdbc_relationships_config_creation(
    jdbc_relationships_configuration, create_jdbc_dataset_definitions, create_relationships
):
    responses.add(
        responses.POST,
        "https://host_name.com/relationshipsConfigurations/",
        json=jdbc_relationships_configuration,
    )

    relationships_configuration = RelationshipsConfiguration.create(
        dataset_definitions=create_jdbc_dataset_definitions, relationships=create_relationships,
    )
    assert responses.calls[0].request.method == "POST"
    assert relationships_configuration.id == "5a530498d5c1f302d6d176c8"
    assert len(relationships_configuration.dataset_definitions) == 1
    assert len(relationships_configuration.relationships) == 2
    definition = relationships_configuration.dataset_definitions[0]
    assert definition["data_source"]["data_store_name"] == "mssql-remote-dev"
    assert definition["data_source"]["data_store_id"] == "60c6e3f833de57c65440f571"
    assert definition["data_source"]["dbtable"] == "safer_credit"
    assert definition["data_source"]["schema"] == "dbo"
    assert definition["data_source"]["catalog"] == "safer"
