# DEPRECATED: please use starthinker/util/sheets/__init__.py

from starthinker.util.sheets import sheets_clear, sheets_write, sheets_batch_update, sheets_read


def trix_update(auth,
                sheet_id,
                sheet_range,
                data,
                clear=False,
                valueInputOption='RAW',
                retries=10):
  print(
      'WARNING: Deprecated "util.trix.trix_update" function, use "util.sheets.sheets_clear" and "util.sheets.sheets_write" instead.'
  )
  sheet_url = 'https://docs.google.com/spreadsheets/d/%s/edit?usp=sharing' % sheet_id
  sheet_tab, sheet_range = sheet_range.split('!', 1)

  if clear:
    sheets_clear(auth, sheet_tab, sheet_range, sheet_url=sheet_url)
  print('S', sheet_url, sheet_tab, sheet_range, data)
  sheets_write(auth, sheet_tab, sheet_range, data, sheet_url=sheet_url)


def trix_batch_update(auth, sheet_id, data, retries=10):
  print(
      'WARNING: Deprecated "util.trix.trix_batch_update" function, use "util.sheets.sheets_batch_update" instead.'
  )
  sheet_url = 'https://docs.google.com/spreadsheets/d/%s/edit?usp=sharing' % sheet_id
  sheets_batch_update(auth, data, sheet_url=sheet_url)


def trix_read(auth, sheet_id, sheet_range, retries=10):
  print(
      'WARNING: Deprecated "util.trix.trix_read" function, use "util.sheets.sheets_read" instead.'
  )
  sheet_url = 'https://docs.google.com/spreadsheets/d/%s/edit?usp=sharing' % sheet_id
  sheet_tab, sheet_range = sheet_range.split('!', 1)
  sheets_read(auth, sheet_tab, sheet_range, sheet_url=sheet_url)
