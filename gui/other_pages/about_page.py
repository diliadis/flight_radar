import streamlit as st

def show():

    personal_website_link = """<a href='https://kermit.ugent.be/phd.php?author=D.%20Iliadis&year=' target="_blank"> <img src='http://www.transmasp.ugent.be/nl/static/icons/favicon-32x32.png'> </a>"""
    linkedin_link = """<a href='https://gr.linkedin.com/in/dimitris-iliadis-a2bb4a113' target="_blank"> <img src='https://cdn.exclaimer.com/Handbook%20Images/linkedin-icon_32x32.png'> </a>"""
    github_link = f"""<a href='https://github.com/diliadis' target="_blank"> <img src='data:images/github_icon.png'> </a>"""

    st.title('About')
    st.write('This is my hobby project I started when I wanted to learn about web scraping')

    st.write('## Contact')
    st.write(f'{personal_website_link} {linkedin_link}', unsafe_allow_html=True)

if __name__ == "__main__":
    show()