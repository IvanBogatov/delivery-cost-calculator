import streamlit as st
from delivery import Delivery

d = Delivery('/workspaces/delivery-cost-calculator/data/data.xlsx')

st.header('Delivery options calculator')
from_city = st.selectbox('Departure City', ['Sydney', 'Melbourne'])
to_post_code = st.number_input('Destination Post Code', value=0)
weight = float(st.number_input('Parcel Weight'))



if st.button('Calculate'):
    best_option, best_certain_option = d.get_delivery_options(from_city, to_post_code, weight)

    if best_option.shape[0] == 0:
        st.write('Incorrect Postal code. Please, try another one.')
    else:
        if best_option.is_overweight.sum() == 1:
            st.write(f"The parcel's weight exceeds the maximum weight specified in the rate schedule. The price is APPROXIMATE. For more information, please contact the delivery service {best_option.Url.values[0]}")

            st.write('Cheapest delivery option.')
            a, b = st.columns(2)
            a.metric(label="Delivery Cost", value=best_option.Cost, border=True)
            b.metric(label="Courier Service", value=best_option.Company.values[0], border=True)
            expander = st.expander("Extra data:")
            expander.dataframe(best_option.drop('is_overweight', axis=1), hide_index=True, column_config={"Url": st.column_config.LinkColumn("Service URL")})

            if best_certain_option.shape[0] != 0:
                st.write("If you don't want contact the delivery service, here is the cheapest certain option.")
                a, b = st.columns(2)
                a.metric(label="Delivery Cost", value=best_certain_option.Cost, delta=f'+${best_certain_option.Cost.values[0]-best_option.Cost.values[0]:.2f}', delta_color='inverse', border=True)
                b.metric(label="Courier Service", value=best_certain_option.Company.values[0], border=True)
                expander = st.expander("Extra data:")
                expander.dataframe(best_certain_option.drop('is_overweight', axis=1), hide_index=True, column_config={"Url": st.column_config.LinkColumn("Service URL")})
        else:
            st.write('Cheapest delivery option.')
            a, b = st.columns(2)
            a.metric(label="Delivery Cost", value=best_option.Cost, border=True)
            b.metric(label="Courier Service", value=best_option.Company.values[0], border=True)
            expander = st.expander("Extra data:")
            expander.dataframe(best_option.drop('is_overweight', axis=1), hide_index=True, column_config={"Url": st.column_config.LinkColumn("Service URL")})
