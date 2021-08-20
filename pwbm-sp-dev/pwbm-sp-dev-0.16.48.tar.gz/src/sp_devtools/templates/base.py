import logging
logging.basicConfig(level=logging.INFO)


# This section needed to provide context locally. Do not change or delete this section
if 'context' not in globals():
    from sp_devtools.context import Context
    context = Context.create_local()


# This function must be present in custom scraper. Please do not delete it. You may add arguments if needed
def custom_scraper_script():
    """Custom script entry point."""
    results_path = context.save_results([], [])
    logging.info(f'Results saved at {results_path}')


# This section is for the local run only and not used during scraper execution on SP
if __name__ == '__main__':
    custom_scraper_script()
