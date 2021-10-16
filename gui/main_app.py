import streamlit as st
from main_components import airline_network_timeline
from other_pages import about_page

app_pages = {
    'Airline Network Visualization': airline_network_timeline.show,
    'About': about_page.show,
}

intro = f"""
This page provides helpful insights from the european flight routes network
"""

def draw_main_page():
    st.title('Flight Network Visualization')
    st.write(intro)

pages = list(app_pages.keys())

if len(pages):
    pages.insert(0, 'Main page')
    st.sidebar.title('menu')
    query_params = st.experimental_get_query_params()
    if 'page' in query_params and query_params['page'][0] == 'headliner':
        idx = 1
    else:
        idx = 0
    selected_app = st.sidebar.radio("", pages, idx)
else:
    selected_app = 'main'

if selected_app in app_pages:
    app_pages[selected_app]()
else:
    draw_main_page()