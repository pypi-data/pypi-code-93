import uuid
import os

from starthinker.util.project import project
from starthinker.util.google_api import API_DCM
from starthinker.util.bigquery import query_to_rows


@project.from_parameters
def publisher_preview():
  if project.verbose:
    print('Publisher Preview')

  profile_id = project.task['profile_id']

  #local_file = '/tmp/%s' % str(uuid.uuid1())
  local_file = '/tmp/%s' % 'test.html'

  out = open(local_file, 'wb')

  out.write('<html><body>')
  out.write('<table border=1>')
  out.write('<tr>')
  out.write(
      '<td><strong>Placement ID</strong></td><td><strong>Placement Name</strong></td><td><strong>Preview</strong></td>'
  )
  out.write('</tr>')

  placements = API_DCM(project.task['auth']).placements().list(
      profileId=profile_id,
      maxResults=5,
      campaignIds=[21097064, 21081031, 21108999, 21115284, 21072124,
                   21074779]).execute()

  for placement in placements['placements']:
    tag = API_DCM(project.task['auth']).placements().generatetags(
        profileId=profile_id,
        campaignId=placement['campaignId'],
        placementIds=[placement['id']],
        tagFormats=['PLACEMENT_TAG_IFRAME_JAVASCRIPT']).execute()

    for placement_tags in tag['placementTags']:
      for tag_datas in placement_tags['tagDatas']:
        out.write('<tr>')
        out.write('<td>%s</td>' % placement['id'])
        out.write('<td>%s</td>' % placement['name'])
        out.write('<td>%s</td>' % tag_datas['impressionTag'])
        out.write('</tr>')

  out.write('</table>')
  out.write('</body></html>')
  out.close()
  #os.path.remove(local_file)


if __name__ == '__main__':
  publisher_preview()
