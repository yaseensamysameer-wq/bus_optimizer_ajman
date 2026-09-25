import streamlit as st
import math
from pathlib import Path
import pandas as pd
import numpy as np
tab1, tab2, tab3 =  st.tabs(['Overview', 'Calender', 'Information'])
with tab1:
    st.title('Bus Optimizer Ajman')
    with st.container:
        st.header('Our mission')
        st.write('Our mission is to make a program that is...')

