import pandas as pd
from sklearn.linear_model import LinearRegression

class Delivery:
    def __init__(self, data_path):
        data = pd.read_excel(data_path, [0,1,2,3,4,5])
        self.data = {
            'Melbourne': [
                {
                    'zones': data[0].drop_duplicates().drop('Country', axis=1),
                    'rates': data[1].drop_duplicates().set_index('Weight').melt(ignore_index=False, var_name='Zone name', value_name='Cost').reset_index().rename(columns={'Weight': 'Weight_tariff'}),
                    'name': 'AU Post Melbourne',
                    'url': 'https://auspost.com.au'
                }
            ],
            'Sydney': [
                {
                    'zones': data[0].drop_duplicates().drop('Country', axis=1),
                    'rates': data[2].drop_duplicates().set_index('Weight').melt(ignore_index=False, var_name='Zone name', value_name='Cost').reset_index().rename(columns={'Weight': 'Weight_tariff'}),
                    'name': 'AU Post Sydney',
                    'url': 'https://auspost.com.au'
                },
                {
                    'zones': data[4].drop_duplicates().drop('Country', axis=1),
                    'rates': data[3].drop_duplicates().set_index('Weight').melt(ignore_index=False, var_name='Zone name', value_name='Cost').reset_index().rename(columns={'Weight': 'Weight_tariff'}),
                    'name': 'Dragonfly Sydney',
                    'url': 'https://dragonflyshipping.com.au'
                }
            ]
        }


    def adjust_costs(self, costs, weight):
        model = LinearRegression()
        model.fit(costs[['Weight_tariff']], costs['Cost'])
        predictions = round(model.predict(pd.DataFrame(data={'Weight_tariff':[weight]}))[0], 2)

        adjustment = costs.iloc[[0]].copy()
        adjustment['Weight_tariff'] = weight
        adjustment['Cost'] = predictions
    
        return pd.concat([costs, adjustment], ignore_index=True).sort_values('Weight_tariff')


    def get_delivery_cost(self, from_city, to_post_code, weight):
        input_df = pd.DataFrame(data={'Postal code': [to_post_code], 'Weight': [weight]})
        options_table = pd.DataFrame()
        for courier_service in self.data[from_city]:
            costs = (
                courier_service['zones'][courier_service['zones']['Postal code'] == to_post_code]
                .merge(courier_service['rates'], how='left')
                .assign(Company = courier_service['name'])
            )
            costs['Url'] = courier_service['url']

            overweight_warn = 0
            if weight > costs.Weight_tariff.max():
                overweight_warn = 1
                costs = self.adjust_costs(costs, weight)

            options_table = pd.concat([
                options_table,
                pd.merge_asof(
                    input_df,
                    costs,
                    by='Postal code',
                    left_on='Weight', 
                    right_on='Weight_tariff', 
                    direction='forward'
                ).assign(is_overweight = overweight_warn)],
                ignore_index=True
                )

        return options_table
    
    def get_delivery_options(self, from_city, to_post_code, weight):
        delivery_options = self.get_delivery_cost(from_city, to_post_code, weight)
        best_option = delivery_options[delivery_options.Cost == delivery_options.Cost.min()]

        if delivery_options.is_overweight.sum() == 0:
            best_certain_option = best_option.copy()
        elif delivery_options.is_overweight.sum() == delivery_options.shape[0]:
            best_certain_option = delivery_options[delivery_options.is_overweight == 2]
        else:
            certain_options = delivery_options[delivery_options.is_overweight == 0]
            best_certain_option = certain_options[certain_options.Cost == certain_options.Cost.min()]

        return best_option, best_certain_option
