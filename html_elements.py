from dash import html
from datetime import date, datetime, timedelta
import dash_mantine_components as dmc
import pandas as pd

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

colors_rgb = {
    'Lectures': 'rgb(132,94,247)',
    'Sketchy': 'rgb(252,196,25)',
    'Anki': 'rgb(92,124,250)',
    'Boards and Beyond': 'rgb(51,154,240)',
    'Bootcamp': 'rgb(255,146,43)',
    'Pathoma': 'rgb(148,216,45)',
    'Other': 'rgb(173,181,189)',
    'Review': 'rgb(204,93,232)',
}

header = html.Div([
    html.Div(
        children = [
            dmc.Title(
                "Things To Do",
                style={'marginRight':'2vw', 'margin':'1vw'}
            ),
            dmc.DatePicker(
                id = 'date-selected',
                value = date.today(),
                style = {
                    'paddingTop': '1vw',
                }
            ),
            html.Div(
                [
                    dmc.RingProgress(
                        id = "ring-progress",
                        sections=[
                            {'value': 40, 'color': 'black'},
                            {'value': 15, 'color': 'black'},
                            {'value': 15, 'color': 'black'},
                        ],
                        size=75,
                    ),
                    dmc.Text(
                        "Welcome Bhargawi!",
                        id='progress-comment',
                        size='sm',
                        style={'margin':'auto'}
                    ),
                ],
                style={'display':'flex', 'margin':'auto'}
            ),
            dmc.Button(
                "Add Task", 
                id = 'add-task-button',
                style={
                    'marginLeft':'auto',
                    'marginRight': '2vw',
                    'marginTop': '1vw'
                }
            )
        ],
        style = {'display': 'flex'}
    ),
])

modal = dmc.Modal(
    id = 'add-task-modal',
    zIndex = 10000,
    children= [
        dmc.TextInput(
            id = {
                'type': 'new-task-info',
                'index': 1
            },
            label='Task Description:',
        ),
        dmc.DatePicker(
            id = {
                'type': 'new-task-info',
                'index': 2
            },
            label = 'Date To Do:',
            value = date.today()
        ),
        dmc.Select(
            id = {
                'type': 'new-task-info',
                'index': 3
            },
            label = 'Select Category',
            data = [
                "Lectures",
                "Sketchy",
                "Anki",
                "Board and Beyond",
                "Bootcamp",
                "Pathoma",
                "Other",
                "Review"
            ]
        ),
        dmc.Space(h=20),
        dmc.Group(
            [
                dmc.Button(
                    "Update Tasks",
                    id='modal-submit'
                ),
                dmc.Button(
                    "Close",
                    color='red',
                    variant='outline',
                    id='modal-close'
                )
            ]
        )
    ]
)

tabs = dmc.Tabs(
    [
        dmc.TabsList(
            [
                dmc.Tab("Today", value='today'),
                dmc.Tab("This Week", value='week'),
            ]    
        ),
        dmc.TabsPanel(id='today-tab',value='today'),
        dmc.TabsPanel(id='week-tab', value='week')
    ],
    value='today',
    style = {
        'marginLeft': '1vw',
        'marginRight': '1vh'
    }
)

take_a_break = html.Div([
    dmc.Text(
        "Nothing to do today!",
        variant='gradient',
        gradient={'from': 'blue', 'to': 'lime', 'deg':  75},
        style={'fontSize': 50}
    ),
    dmc.Center(dmc.Image(
        src="/assets/images/sleep-nitez.gif",
        width=250
    )),
    dmc.Text(
        "Take a break ;)",
        variant='gradient',
        gradient={'from': 'blue', 'to': 'lime', 'deg':  75},
        style={'fontSize': 50}
    ),
],style={'textAlign':'center'})

def today_schedule(dfs, length):
    return dmc.SimpleGrid(
        cols=3,
        children=[to_do_card(dfs[c], c) for c in dfs.keys()],
        style={
            'marginTop': '2vh'
        }
    )

def to_do_card(data, category):
    if data[0].empty:
        checklist = [
            dmc.Text(
                "Nothing for today!",
                color = colors[category],
                ta = 'center',
                fw = 500,
                fz = 15
            )
        ]
    else:
        checklist = []
        n = data[1]
        for index, row in data[0].iterrows():
            checklist.append(
                dmc.Chip(
                id = {
                        'type': 'chip',
                        'index': n
                    },
                    children = row['Task'],
                    color=colors[category],
                    checked=row['Completed'],
                    p = 7.5,
                    pl = 15
                )
            )
            n += 1
    return dmc.Card(
        [
            dmc.CardSection(
                dmc.Text(
                    category, 
                    color='white', 
                    weight=500,
                    fz=20,
                    align='center',
                ),
                bg = colors[category],
            ),
            dmc.CardSection(
                checklist,
                id = {
                    'type': 'checklist',
                    'index': category
                }
            )
        ],
        withBorder=True,
        shadow='sm',
        radius='md'
    )

def week_breakdown(date, df):
    dt = datetime.strptime(date, '%Y-%m-%d')
    dates = []
    for r in range(7):
        td = r - dt.weekday()
        dates.append((dt + timedelta(td)).strftime('%Y-%m-%d'))
    df_week = df[df['Date'].isin(dates)]
    return html.Div(
        children=[ 
            dmc.Table(
                table_header() + table_body(dates, df_week),
                horizontalSpacing='xs',
                highlightOnHover=True,
                striped=True,
            )
        ],
        style={
            'marginTop': '2vh'
        }
    )

def table_header():
    table_cols = [
        html.Th("Date"),
        html.Th("Day"),
    ]
    for cat in colors.keys():
        table_cols.append(
            html.Th(cat, style={'color':colors_rgb[cat]})
        )
    table_cols.append(html.Th("Blah", style={'color':'white'}))
    return [html.Thead(html.Tr(table_cols))]

def table_body(dates, df):
    rows = []
    days=['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday']
    for d in dates:
        r = [
            html.Td(d),
            html.Td(days[datetime.strptime(d, '%Y-%m-%d').weekday()]),
        ]
        temp_df = df[df['Date']==d]
        for cat in colors.keys():
            temp_dff = temp_df[temp_df['Category']==cat]
            r.append(html.Td(to_data(temp_dff['Task'], temp_dff['Completed'],colors[cat])))
        rows.append(html.Tr(r))
    return [html.Tbody(rows)]

def to_data(tasks, done, color):
    if tasks.empty:
        return ''
    c = []
    for index, val in tasks.items():
        c.append(
            dmc.Checkbox(
                label="{}".format(val),
                checked=done[index],
                #disabled=True,
                color=color,
                m=5
            )
        )
    return html.Div(c)