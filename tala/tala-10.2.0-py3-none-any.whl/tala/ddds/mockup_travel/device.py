# -*- coding: utf-8 -*-

from tala.model.device import DddDevice, DeviceWHQuery, DeviceAction, Validity, DeviceImplication, EntityRecognizer
from tala.model.proposition import PredicateProposition


class MockupTravelDevice(DddDevice):

    CITY_COUNTRY = {"london": "england", "paris": "france", "lyon": "france"}
    CITY_TYPE = {"paris": "city_type_capital", "lyon": "non_capital"}

    def __init__(self):
        self._dept_city_value = None
        self._dept_city_confidence = None
        self._dept_city_grammar_entry = None

    def get_available_dept_cities(self, dest_city_grammar_entry):
        results = [{"name": "city_madrid", "grammar_entry": "Madrid"}]
        if dest_city_grammar_entry not in ["Athens", "آتن"]:
            results.append({"name": "city_helsinki", "grammar_entry": "Helsinki"})
        results.append({"grammar_entry": "New York"})
        return results

    class dest_city(DeviceImplication):
        ANTECEDENT = "dest_city"

        def imply(self, dest_city):
            implications = []
            if dest_city in MockupTravelDevice.CITY_COUNTRY:
                country_name = MockupTravelDevice.CITY_COUNTRY[dest_city]
                implications.append(
                    PredicateProposition(
                        self.ontology.get_predicate("dest_country"), self.ontology.create_individual(country_name)
                    )
                )
            if dest_city in MockupTravelDevice.CITY_TYPE:
                type_name = MockupTravelDevice.CITY_TYPE[dest_city]
                implications.append(
                    PredicateProposition(
                        self.ontology.get_predicate("dest_city_type"), self.ontology.create_individual(type_name)
                    )
                )
            return implications

    class available_dept_city(DeviceWHQuery):
        def perform(self, dest_city_grammar_entry):
            return self.device.get_available_dept_cities(dest_city_grammar_entry)

    class selected_housing(DeviceWHQuery):
        def perform(self, selected_housing_type, selected_housing_rating):
            return [{"name": "sheraton", "grammar_entry": "Sheraton"},
                    {"name": "novotel", "grammar_entry": "Novotel"}]

    class selected_housing_for_contact(selected_housing):
        pass

    class selected_housing_for_pets(DeviceWHQuery):
        def perform(self, selected_housing_type, selected_housing_rating):
            return []

    class selected_housing_for_moomins(selected_housing):
        pass

    class available_member_type(DeviceWHQuery):
        def perform(self):
            return []

    class num_available_dept_cities(DeviceWHQuery):
        def perform(self, dest_city_grammar_entry):
            return [len(self.device.get_available_dept_cities(dest_city_grammar_entry))]

    class code(DeviceWHQuery):
        def perform(self):
            return ["XL34"]

    class frequent_flyer_number(DeviceWHQuery):
        def perform(self):
            return ["123-456"]

    class available_payment_method(DeviceWHQuery):
        def perform(self):
            return ["visa", "mastercard", "points"]

    class price(DeviceWHQuery):
        def perform(self, means_of_transport, dest_city, dept_city, dept_month, dept_day, class_):
            if dest_city is not None and dept_city is not None:
                return [1234.0]
            else:
                return []

    class MakeReservation(DeviceAction):
        def perform(self, dest_city, dept_city):
            if dest_city == dept_city:
                self.failure_reason = "dest_city_same_as_dept_city"
                return False
            else:
                return True

    class MakeRandomReservation(DeviceAction):
        def perform(self):
            return True

    class CityTypeValidity(Validity):
        def is_valid(self, city, city_type):
            if self.device.CITY_TYPE[city] == city_type:
                return True
            else:
                return False

    class CityValidity(Validity):
        def is_valid(self, city, city_grammar_entry):
            return city != "pyongyang" and city_grammar_entry != "Lisbon" and city_grammar_entry != "لیزبون"

    def set_dept_city_value(self, value):
        self._dept_city_value = value

    def set_dept_city_confidence(self, confidence):
        self._dept_city_confidence = confidence

    def set_dept_city_grammar_entry(self, grammar_entry):
        self._dept_city_grammar_entry = grammar_entry

    class dept_city(DeviceWHQuery):
        def perform(self):
            if self.device._dept_city_value:
                return [{
                    "name": self.device._dept_city_value,
                    "confidence": self.device._dept_city_confidence,
                    "grammar_entry": self.device._dept_city_grammar_entry
                }]
            else:
                return []

    class CityRecognizer(EntityRecognizer):
        def recognize(self, string, language):
            string = string.lower()
            results = []
            if "buenos aires" in string:
                results.append({"sort": "city", "grammar_entry": "Buenos Aires"})
            if "oslo" in string:
                results.append({"sort": "city", "grammar_entry": "Oslo"})
            if "new york" or "nueva york" in string:
                results.append({"sort": "city", "grammar_entry": "New York"})
            if "reykjavik" in string:
                results.append({"sort": "city", "grammar_entry": "Reykjavik"})
            if "lisbon" in string:
                results.append({"sort": "city", "grammar_entry": "Lisbon"})
            if "göteborg" in string:
                results.append({"name": "city_gbg", "sort": "city", "grammar_entry": "Göteborg"})
            if "örebro" in string:
                results.append({"name": "city_orebro", "sort": "city", "grammar_entry": "Örebro"})
            if "varberg" in string:
                results.append({"name": "Varberg", "sort": "city", "grammar_entry": "Varberg"})
            if "لیزبون" in string:
                results.append({"sort": "city", "grammar_entry": "لیزبون"})
            if "بوینس آیرس" in string:
                results.append({"sort": "city", "grammar_entry": "بوینس آیرس"})
            if not string:
                results.append({"name": "city_empty", "sort": "city", "grammar_entry": ""})
            return results

    class LanguageSpecificCityRecognizer(EntityRecognizer):
        def recognize(self, string, language):
            string = string.lower()
            results = []
            if language == "eng":
                if "athens" in string:
                    results.append({"sort": "city", "grammar_entry": "Athens"})
            elif language == "sv":
                if "aten" in string:
                    results.append({"sort": "city", "grammar_entry": "Aten"})
            elif language == "spa":
                if "atenas" in string:
                    results.append({"sort": "city", "grammar_entry": "Atenas"})
            if language == "pes":
                if "آتن" in string:
                    results.append({"sort": "city", "grammar_entry": "آتن"})
            return results

    class MeansOfTransportRecognizer(EntityRecognizer):
        def recognize(self, string, language):
            if string == "shuttle":
                return [{"sort": "how"}]

    class KeywordRecognizer(EntityRecognizer):
        def recognize(self, string, language):
            if string == "vacation":
                return [{"sort": "keyword", "grammar_entry": "vacation"}]
            if "0" in string:
                return [{"sort": "keyword", "grammar_entry": "0"}]

    class passenger_quantity_to_add(DeviceWHQuery):
        def perform(self):
            return [1]

    class AddPassengers(DeviceAction):
        def perform(self, passenger_types, quantity):
            return True

    class available_means_of_transport(DeviceWHQuery):
        def perform(self):
            return ["plane", "train"]

    class qualified_for_membership(DeviceWHQuery):
        def perform(self, dest_city):
            if dest_city == "pyongyang":
                return []
            else:
                return [True]

    class frequent_flyer_points(DeviceWHQuery):
        def perform(self):
            return [50]

    class current_position(DeviceWHQuery):
        def perform(self):
            return [{"name": "london", "grammar_entry": "london"}]

    class CancelReservation(DeviceAction):
        def perform(self):
            return True

    class next_membership_level(DeviceWHQuery):
        def perform(self):
            return ["silver"]

    class selected_train_type(DeviceWHQuery):
        def perform(self):
            return ["electrical"]

    class next_membership_points(DeviceWHQuery):
        def perform(self):
            return [50]

    class BookHousing(DeviceAction):
        def perform(self):
            return True

    class room_availability(DeviceWHQuery):
        def perform(self, room_type):
            return [True]

    class RegisterComment(DeviceAction):
        def perform(self, comment_message, comment_name):
            return True

    class attraction_information(DeviceWHQuery):
        def perform(self, attraction):
            if "Eiffel tower" in attraction:
                return ["the eiffel tower is a wrought iron lattice tower on the " + "champ de mars in paris, france"]
            elif "ایفل" in attraction:
                return ["برج ایفل یک برج مشبک فلزی در پاریس است"]
            else:
                return ["no information was found"]

    class house_owner_name(DeviceWHQuery):
        def perform(self):
            return ["Örjan"]

    class need_visa(DeviceWHQuery):
        def perform(self, dept_city, dest_city):
            def within_eu(dept_city, dest_city):
                cities_outside_eu = ["Pyongyang", "New York"]
                return dept_city not in cities_outside_eu and dest_city not in cities_outside_eu
            need_visa = not within_eu(dept_city, dest_city)
            return [need_visa]

    class flight_departure(DeviceWHQuery):
        def perform(self):
            return ["2018-04-11T22:00:00.000Z"]

    class flight_on_time(DeviceWHQuery):
        def perform(self):
            return ["on time"]

    class flight_exists(DeviceWHQuery):
        def perform(self):
            return ["a connection"]
