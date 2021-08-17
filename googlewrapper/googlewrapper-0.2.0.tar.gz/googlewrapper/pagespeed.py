import requests
from urllib.parse import urlparse
from pandas import DataFrame
from datetime import date


class PageSpeed:
    def __init__(self, key):
        self._key = key
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?"
        self.set_category()
        self.date = date.today()

    def set_url(self, url) -> None:
        def url_validation(url):
            try:
                result = urlparse(url)
                return all([result.scheme, result.netloc, result.path])
            except ValueError:
                return False

        if url_validation(url):
            self.url = url
        else:
            raise ValueError(f"{url} is not a valid URL")

    def set_device(self, device) -> None:
        device_list = ["DESKTOP", "MOBILE"]
        if device.upper() in device_list:
            self.device = device.upper()
        else:
            raise ValueError(
                f"{device} is not a valid device type."\
                f" Try one of the following: {device_list}"
            )

    def set_category(self, category="PERFORMANCE") -> None:
        category_list = ["ACCESSIBILITY", 
                        "BEST_PRACTICES", 
                        "PERFORMANCE", 
                        "PWA", 
                        "SEO"
                        ]
        if category.upper() in category_list:
            self.category = category.upper()
        else:
            raise ValueError(
                f"{category} is not a valid category type."\
                f" Try on of the following: {category_list}"
            )

    def pull(self, output="df") -> DataFrame:
        try:
            request_string = (
                f"category={self.category}"
                f"&url={self.url}"
                f"&strategy={self.device}"
                f"&key={self._key}"
            )
        except AttributeError as e:
            issue = e.args[0].split("'")[-2]
            raise AttributeError(
                f"Please assign the variable"\
                f" {issue} using self.set_{issue}()"
            )
        if output == "df":
            return self.create_df(requests.get(self.base_url + request_string).json())
        else:
            return requests.get(self.base_url + request_string).json()

    def create_df(self, results) -> DataFrame:
        # Performance Score
        performance_score = results["lighthouseResult"]["categories"]\
            ["performance"]["score"]
        # Largest Contenful Paint
        largest_contentful_paint = results["lighthouseResult"]["audits"]\
            ["largest-contentful-paint"]["numericValue"]

        # First Input Delay
        first_input_delay = int(
            round(
                results["loadingExperience"]["metrics"]
                    ["FIRST_INPUT_DELAY_MS"]["distributions"][2]\
                    ["proportion"]* 1000,
                1,
            )
        )
        # CLS
        cumulative_layout_shift = results["lighthouseResult"]["audits"]\
            ["cumulative-layout-shift"]["displayValue"]

        # Largest Contenful Paint Score
        crux_lcp = results["loadingExperience"]["metrics"]\
            ["LARGEST_CONTENTFUL_PAINT_MS"]["category"]

        # First Input Delay Score
        crux_fid = results["loadingExperience"]["metrics"]\
            ["FIRST_INPUT_DELAY_MS"]["category"]

        # CLS Score
        crux_cls = results["loadingExperience"]["metrics"]\
            ["CUMULATIVE_LAYOUT_SHIFT_SCORE"]["category"]

        # format as list for entry into pd.DF
        score_data = [
            self.url,
            self.device,
            self.date,
            performance_score,
            largest_contentful_paint,
            first_input_delay,
            cumulative_layout_shift,
            crux_lcp,
            crux_fid,
            crux_cls,
        ]
        cols = [
            "URL",
            "DEVICE",
            "DATE",
            "PERFORMANCE_SCORE",
            "LCP",
            "FID",
            "CLS",
            "LCP_SCORE",
            "FID_SCORE",
            "CLS_SCORE",
        ]
        return DataFrame([score_data], columns=cols)