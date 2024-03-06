import datetime

import matplotlib.pyplot as plt
import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


st.set_page_config(
    page_title="RSUs calculator",
    page_icon="📈",
)


class RSU:
    def __init__(
        self,
        name: str,
        date: datetime.date,
        total: float,
        duration_years: int,
        cliff_years: int,
    ):
        self.name = name
        self.date = date
        self.total = total
        self.duration_years = duration_years
        self.cliff_days = 365 * cliff_years
        self.amounts = self.compute_amounts()

    @staticmethod
    def get_next_date(date: datetime.date):
        next_month = date.month + 3
        if next_month > 12:
            return datetime.date(date.year + 1, next_month - 12, date.day)
        else:
            return datetime.date(date.year, next_month, date.day)

    def compute_amounts(self) -> dict[datetime.date, float]:
        # end_date = self.date + datetime.timedelta(days=365 * self.duration_years + 90)
        end_date = datetime.date(year=2030, month=12, day=31)
        amounts = {}
        vested = 0
        date = self.date
        next_date = RSU.get_next_date(date)
        increase_percentage = 100 / self.duration_years / 4
        acc_percentage = increase_percentage
        while True:
            if date == next_date:
                if date < self.date + datetime.timedelta(days=self.cliff_days):
                    acc_percentage += increase_percentage
                elif vested < self.total:
                    vested += self.total * acc_percentage / 100
                    acc_percentage = increase_percentage
                next_date = RSU.get_next_date(next_date)
            amounts[date] = vested
            date += datetime.timedelta(days=1)
            if date == end_date:
                break
        return amounts


def update():
    fig, axis = plt.subplots(figsize=(10, 5))

    try:
        st.session_state.rsus[name] = RSU(
            name,
            start_date,
            total,
            duration_years,
            cliff_years,
        )
    except Exception as e:
        LOGGER.error(e)
        st.write(str(e))
        return

    def plot_amounts(amounts: dict[datetime.date, float], name: str, color=None):
        dates = list(amounts.keys())
        values = list(amounts.values())
        axis.plot(dates, values, label=name, color=color)

    for rsu_name, rsu in st.session_state.rsus.items():
        plot_amounts(rsu.amounts, rsu_name)

    amounts = [rsu.amounts for rsu in st.session_state.rsus.values()]
    if len(amounts) > 1:
        all_amounts = add_dicts(*amounts)
        plot_amounts(all_amounts, 'Total', color='black')
    axis.legend()
    axis.grid()
    st.pyplot(fig)


def add_dicts(*dicts) -> dict:
    all_keys = set()
    for d in dicts:
        all_keys.update(d.keys())
    result = {}
    for k in sorted(all_keys):
        result[k] = sum(d.get(k, 0) for d in dicts)
    return result


if __name__ == '__main__':
    if 'rsus' not in st.session_state:
        st.session_state.rsus = {}
    st.markdown("# RSUs")
    st.sidebar.header("RSUs")
    st.write('Test')

    name_col, total_col, start_col, duration_col, cliff_col, add_col = st.columns(6)

    name = name_col.text_input('Award name')
    total = total_col.number_input('Total k$') * 1000
    start_date = start_col.date_input('Start date')
    duration_years = duration_col.number_input('Duration years', value=5)
    cliff_years = cliff_col.number_input('Cliff years', value=0)
    add_col.button('Add', on_click=update)
