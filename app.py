from dash import Dash, dcc, ctx, html, callback, ALL, Output, Input, State, MATCH, no_update
from dash.exceptions import PreventUpdate
import pandas as pd

from html_elements import (header, modal, tabs, take_a_break,
                            today_schedule, week_breakdown)

app = Dash(__name__)
#server = app.server #uncomment during push

app.layout = html.Div([
    header,
    modal,
    tabs,
    dcc.Store( # store tasks
        id = 'tasks-data',
        data = pd.read_csv('sched.csv').to_dict('records')
    ),
    dcc.Store( # new task temp
        id = 'new-task-data',
        data = None
    ),
    dcc.Store(
        id = 'temp-holder',
        data = None
    ),
    # add more stuff
])

@app.callback(
    Output('add-task-modal', 'opened'),
    Input('add-task-button', 'n_clicks'),
    Input('modal-submit', 'n_clicks'),
    Input('modal-close', 'n_clicks'),
    State('add-task-modal', 'opened'),
    prevent_initial_call=True
)
def open_close_modal(n1, n2, n3, opened):
    return not opened

@app.callback(
    Output('tasks-data', 'data'),
    Input('new-task-data', 'data'),
    Input('temp-holder', 'data'),
    State('tasks-data', 'data'),
    prevent_initial_call=True
)
def update_task_data(new_row, new_data, tasks_data):
    triggered = ctx.triggered_id
    if triggered == 'new-task-data' and new_row is not None:
        print('Adding row {}'.format(new_row[0]))
        tasks_data.append(new_row[0])
        return tasks_data
    elif triggered == 'temp-holder' and new_data is not None:
        return new_data
    else:
        return no_update

@app.callback(
    Output('new-task-data', 'data'),
    Output({'type': 'new-task-info', 'index': 1}, 'value'),
    Output({'type': 'new-task-info', 'index': 3}, 'value'),
    Input('modal-submit', 'n_clicks'),
    State({'type': 'new-task-info', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def add_task(n, values):
    if None in values:
        raise PreventUpdate
    new_row = {
        'Task': values[0],
        'Date': values[1],
        'Category': values[2],
        'Completed': False
    }
    return [new_row], None, None

@app.callback(
    Output('today-tab', 'children'),
    Output('week-tab', 'children'),
    Input('date-selected', 'value'),
    Input('tasks-data', 'data')
)
def d(selected_date, tasks_data):
    tasks_df = pd.DataFrame(tasks_data)
    df = tasks_df[tasks_df["Date"] == selected_date]
    if df.empty:
        return take_a_break, week_breakdown(selected_date, tasks_df)
    return [
        today_schedule(categorize(df), len(df)), 
        week_breakdown(selected_date, tasks_df)
    ]

@app.callback(
    Output('ring-progress', 'sections'),
    Output('progress-comment', 'children'),
    Output('temp-holder', 'data'),
    Input({'type': 'chip', 'index': ALL}, 'checked'),
    State({'type': 'chip', 'index': ALL}, 'children'),
    State('tasks-data', 'data'),
    State('date-selected', 'value'),
    prevent_initial_call=True
)
def mark_done(checked, task, tasks_data, selected_date):
    triggered_ind = ctx.triggered_id
    if triggered_ind is None:
        return [
            [{'value':100, 'color':'#D3D3D3'}],
            "z z z . . .",
            None
        ]
    triggered_ind = triggered_ind['index']
    checked = checked[triggered_ind]
    task = task[triggered_ind]
    tasks_df = pd.DataFrame(tasks_data)
    tasks_td_df = tasks_df[tasks_df['Date']==selected_date]
    index = tasks_td_df[tasks_td_df['Task']==task].index[0]
    if checked:
        tasks_df.at[index, 'Completed'] = True
    else:
        tasks_df.at[index, 'Completed'] = False
    tasks_td_df = tasks_df[tasks_df['Date']==selected_date]
    done = len(tasks_td_df[tasks_td_df['Completed']==True])
    return [
        amt_done(tasks_td_df),
        get_comment((done/len(tasks_td_df))*100),
        tasks_df.to_dict('records'),
    ]

# Local functions

def categorize(df):
    dfs = {}
    n = 0
    card_names = [
        'Lectures', 'Sketchy', 'Anki', 'Boards and Beyond', 
        'Bootcamp', 'Pathoma', 'Other', 'Review',
    ]
    for cat in card_names:
        dff = df[df['Category']==cat]
        dfs[cat] = [dff, n]
        n += len(dff)
    return dfs

def amt_done(df):
    total = len(df)
    sections = []
    colors = {
        'Lectures': 'violet',
        'Sketchy': 'yellow',
        'Anki': 'indigo',
        'Boards and Beyond': 'blue',
        'Bootcamp': 'orange',
        'Pathoma': 'lime',
        'Other': 'grey',
        'Review': 'grape',
    }
    for name in colors.keys():
        n = len(df[(df['Category']==name) & (df['Completed']==True)])
        sections.append(
            {
                'value': (n / total) * 100,
                'color': colors[name]
            }
        )
    return sections

def get_comment(done):
    if done == 0:
        return "Time to get started!"
    elif done < 30:
        return "Great start, keep it up!"
    elif done < 55:
        return "Almost halfway there!"
    elif done < 65:
        return "Halfway there, love..."
    elif done < 75:
        return "Woooooohoooooooo"
    elif done < 85:
        return "You got this babes!"
    elif done < 90:
        return "You're doing AMAZING"
    elif done < 99:
        return "Almost done !!!"
    else:
        return "Good Job! Now give me attention"

if __name__ == '__main__':
    app.run(debug=True)

