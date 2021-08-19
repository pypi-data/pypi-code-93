# Queries related to managing the collector

GENERATE_COLLECTOR_TEMPLATE = """
mutation generateCollectorTemplate($region:String) {
  generateCollectorTemplate(region:$region) {
    dc {
      templateLaunchUrl
      stackArn
      customerAwsAccountId
      active
      apiGatewayId
    }
  }
}
"""
