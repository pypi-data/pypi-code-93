"""This module contains the market agent model for the qmarket
Author: Torge Wolff <torge.wolff@offis.de>

"""
import math
import datetime
import pandas as pd

from midas.adapter.market_agents import LOG


class MarketAgentModel:
    def __init__(
        self,
        sid,
        eid,
        unit_type,
        s_max,
        start_date,
        step_size=15 * 60,
        date_fmt="%Y-%m-%d %H:%M:%S%z",
    ):
        self.sid = sid
        self.eid = eid
        self.unit_type = unit_type
        self.s_max = s_max
        self.step_size = step_size
        self.start_date = datetime.datetime.strptime(start_date, date_fmt)
        self.current_date = self.start_date
        self.next_offer_date = self.current_date + datetime.timedelta(
            seconds=self.step_size
        )
        self.last_offer_date = None
        self.reactive_power_offer = None
        self.set_q_schedule = None
        self.place_offer_state = True
        internal_schedule_columns = [
            "p_mw",
            "q_mvar",
            "q_min",
            "q_max",
            "q_offer",
            "sent_q_offer",
            "q_target",
        ]
        self.internal_schedule = pd.DataFrame(
            columns=internal_schedule_columns
        )

    def create_q_offer(self, time, schedule=None, sim_place_offer_state=True):
        """Create q_offer for q market operator by using schedule from
        unit.

        """
        self.current_date = self.start_date + datetime.timedelta(seconds=time)
        self.place_offer_state = sim_place_offer_state
        LOG.info(
            "[{}] Step at current time: {}".format(self.eid, self.current_date)
        )

        # check if agent must create q_offer
        if time == 0:
            create_offer = True
        # create offer every self.step_size iterations
        elif time % self.step_size == 0:
            create_offer = True
        elif self.place_offer_state:
            create_offer = True
        else:
            LOG.info("[{}] No need to create q_offer!".format(self.eid))
            create_offer = False

        if create_offer:
            LOG.info("[{}] Create new q_offer".format(self.eid))
            self._update_internal_schedule(schedule)
            self._create_reactive_power_offer()
            self.last_offer_date = self.next_offer_date
            # update next offer time
            self.next_offer_date = self.last_offer_date + datetime.timedelta(
                seconds=self.step_size
            )
            LOG.info(
                "[{}] Next offer will be generated at: {}".format(
                    self.eid, self.next_offer_date
                )
            )

    def set_q_values(
        self, time, q_set_minutes_15_to_30=None, sim_place_offer_state=False
    ):
        """Set q values from q market operator."""
        self.current_date = self.start_date + datetime.timedelta(seconds=time)
        self.place_offer_state = sim_place_offer_state
        LOG.info(
            "[{}] Step at current time: {}".format(self.eid, self.current_date)
        )

        if (
            q_set_minutes_15_to_30 is not None
            and self.place_offer_state is False
        ):
            LOG.info(
                "[{}] Set q_target Value with value: {}!".format(
                    self.eid, q_set_minutes_15_to_30
                )
            )
            self._set_q_target_value(q_set_minutes_15_to_30)
            LOG.info(
                "[{}] Internal Schedule:\n {}".format(
                    self.eid, self.internal_schedule
                )
            )

    def _set_q_target_value(self, q_set_minutes_15_to_30):
        q_max = self.internal_schedule["q_max"].loc[self.last_offer_date]
        q_target = q_set_minutes_15_to_30 / q_max
        tmp_schedule = {"target": q_target}
        self.set_q_schedule = pd.DataFrame(
            tmp_schedule, index=pd.to_datetime([self.last_offer_date])
        )
        self.internal_schedule.at[self.last_offer_date, "q_target"] = q_target
        LOG.info(self.set_q_schedule)

    def _update_internal_schedule(self, schedule):
        LOG.info(
            "[{}] Schedule from unit is:  \n{}".format(self.eid, schedule)
        )
        p_mw_next_15_minutes = schedule["p_mw"].loc[self.next_offer_date] * -1
        q_mvar_next_15_minutes = (
            schedule["q_mvar"].loc[self.next_offer_date] * -1
        )

        schedule_update = {
            "p_mw": p_mw_next_15_minutes,
            "q_mvar": q_mvar_next_15_minutes,
            "sent_q_offer": False,
            "q_min": None,
            "q_max": None,
            "q_offer": None,
            "q_target": None,
        }
        # noinspection PyTypeChecker
        tmp_df = pd.DataFrame(
            schedule_update, index=pd.to_datetime([self.next_offer_date])
        )
        self.internal_schedule = self.internal_schedule.append(tmp_df)

    def _create_reactive_power_offer(self):
        """Create an offer (tupel) with dicts of q_min, q_max and
        q_price values.

        """

        LOG.info(
            "[{}] Create offer to qmarket for time: {}".format(
                self.eid, self.next_offer_date
            )
        )
        self._calculate_q_min_and_q_max()
        self._calculate_linear_q_price()
        self.reactive_power_offer = (
            {
                "agent_id": f"{self.sid}.{self.eid}",
                "q_min": self.internal_schedule["q_min"].loc[
                    self.next_offer_date
                ],
                "q_max": 0,
                "q_price": self.q_price_per_mvarh_eur * -1,
            },
            {
                "agent_id": f"{self.sid}.{self.eid}",
                "q_min": 0,
                "q_max": self.internal_schedule["q_max"].loc[
                    self.next_offer_date
                ],
                "q_price": self.q_price_per_mvarh_eur,
            },
        )

        self.internal_schedule.at[self.next_offer_date, "sent_q_offer"] = True
        LOG.info(
            "[{} Q-Offer for time {} is:\n{}".format(
                self.eid, self.next_offer_date, self.reactive_power_offer
            )
        )

    def _calculate_q_min_and_q_max(self):
        """Calculate q_min and q_max by s_max of each unit"""
        p_mw_next_15 = self.internal_schedule["p_mw"].loc[self.next_offer_date]
        q_max = math.sqrt(p_mw_next_15 ** 2 + self.s_max ** 2)
        self.internal_schedule.at[self.next_offer_date, "q_max"] = q_max
        self.internal_schedule.at[self.next_offer_date, "q_min"] = q_max * -1

    def _calculate_linear_q_price(self):
        """Calculate lineare price with fixed value."""
        # TODO: Search for different prices per unit type and make non-static.

        # The unit is EUR/MVArh
        # https://bit.ly/3edHkXT
        # p. 109
        self.q_price_per_mvarh_eur = 0.52
