from aleksis.core.util.apps import AppConfig


class HjelpConfig(AppConfig):
    name = "aleksis.apps.hjelp"
    verbose_name = "AlekSIS — Hjelp (Support)"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official/AlekSIS-App-Hjelp/",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        ([2019, 2020, 2021], "Jonathan Weth", "dev@jonathanweth.de"),
        ([2019, 2020, 2021], "Julian Leucker", "leuckeju@katharineum.de"),
        ([2019, 2020], "Hangzhi Yu", "yuha@katharineum.de"),
        ([2019], "Frank Poetzsch-Heffter", "p-h@katharineum.de"),
        ([2020], "Dominik George", "dominik.george@teckids.org"),
        ([2020], "Tom Teichler", "tom.teichler@teckids.org"),
    )
