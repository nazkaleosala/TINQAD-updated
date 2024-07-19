import hashlib

import dash
from dash import callback_context, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps import dbconnect as db
 



layout = dbc.Row(
    [
        dbc.Col(
            html.Div(
            [
                html.Div(  
                            [
                                dcc.Store(id='user_id_store', storage_type='session', data=0),
                            ]
                        ),
                
                html.Div(
                    [
                        html.Img(src=app.get_asset_url('icons/qao-logo-block.png'),
                                style = {
                                    'max-width': '25vw',
                                    'margin': 'auto',  # Center the image horizontally
                                    'display': 'block'  # Make sure it's displayed as a block element
                                },
                        ),
                        html.H5("Total Integrated Network for Quality Assurance and Development", className="fw-bolder text-center"),
                        html.P("Copyright (c) 2024. Quality Assurance Office, University of the Philippines", className="text-center"),
                   
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.A("About TINQAD", href="/about-us", className="link-style"), " | ",
                                        html.A("Main Website", href="https://qa.upd.edu.ph/", className="link-style"), " | ",
                                        html.A("Facebook", href="https://www.facebook.com/QAODiliman", className="link-style"), " | ",
                                        html.A("LinkedIn", href="https://www.linkedin.com/company/quality-assurance-office/about/", className="link-style")
                                    ],
                                    width = "auto"
                                ),
                            ],
                            style = {'margin' : 'auto'},
                            align = 'center', justify = 'center'
                        ),
                    ],
                    style = {
                        'top': '10rem',
                        'right': '25rem',
                        'position': 'relative',   
                        'z-index': 1,
                        'max-width': '70vw',
                        'margin': 'auto',
                        'text-align': 'center',
                        'padding': '2em',
                        
                    }
                ),




                html.Div(
                    [
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H2("LOG IN", className="card-title fw-bolder "),
                                        html.Br(),
 
                                            dbc.Alert(id='login_alert', is_open=False),  
                                            
                                            dbc.Label("Registered Email"),
                                            dbc.Input(type="text", id="login_username", ),
                                            html.Br(),
                                            
                                            dbc.Label("Password"),
                                            dbc.Input(type="password", id="login_password"),
                                            html.Br(),
                                            dbc.Checklist(
                                                options=[
                                                    {"label": "Show Password", "value": 1},
                                                ],
                                                value=[],
                                                id="show_password",
                                                inline=True,
                                            ),
                                            html.Br(), 
                                            dbc.Row(
                                                dbc.Col(
                                                    dbc.Button("Log in",
                                                            color="primary",
                                                            className="fw-bolder",
                                                            id='login_loginbtn'),
                                                    width={'size': 4, 'offset': 8},
                                                    className="d-flex justify-content-end"
                                                )
                                            ),
                                            html.Br(),
                                            html.Br(),
                                            html.H4("Total Integrated Network for Quality Assurance and Development", className="fw-bolder text-danger"),
                                            html.P("The Total Integrated Network for Quality Assurance and Development (TINQAD) is a centralized network that allows the singular monitoring of the Quality Assurance teams activities."),
                                        ]
                                        ),
                                    ),
                                    width={"size": 6, "offset": 1},
                                    style={
                                        'position': 'fixed',
                                        'right': '2rem',  # Position the div at the right of the screen
                                        'width': '45%',  # Set the width of the div
                                        'bottom': '0rem',  # Adjusted bottom margin
                                        'top': '5rem',
                                        'padding': '1rem',
                                        'border-radius': '10px',
                                        'box-shadow': '0px 0px 10px rgba(0, 0, 0, 0.1)',  # Add box shadow
                                    }
                                ),
                            ]
                        ),
                    ],
            id='bg',
            style={
                'position': 'fixed',
                'top': '3.5rem',  # Adjust the top margin as needed
                'left': '0',
                'width': '100%',
                'height': '100%',
                'min-height': 'calc(100% + 20rem)',  # Set a minimum height to ensure content is scrollable
                'background-image': 'url("' + app.get_asset_url('icons/bg.png') + '")',
                'background-size': 'cover',
                'background-position': 'center bottom',
                'mask-image': 'linear-gradient(to bottom, rgba(0, 0, 0, 1.0) 50%, transparent 100%)',
                
            }
        ),
        ),
    ]
)


app.clientside_callback(
    """
    function(n_clicks, n_key_presses) {
        var passwordField = document.getElementById('login_password');
        passwordField.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                document.getElementById('login_loginbtn').click();
            }
        });
    }
    """,
    Output('login_loginbtn', 'n_clicks'),
    [Input('login_password', 'n_key_presses')],
    [State('login_loginbtn', 'n_clicks')]
)

@app.callback(
    [
        Output('login_alert', 'color'),
        Output('login_alert', 'children'),
        Output('login_alert', 'is_open'),
        Output('currentuserid', 'data'),
        Output('currentrole', 'data'),  
        Output('url', 'pathname'),  # Adding URL pathname output
    ],
    [
        Input('login_loginbtn', 'n_clicks')
    ],
    [
        State('login_username', 'value'),
        State('login_password', 'value'), 
        State('currentuserid', 'data'), 
        State('url', 'pathname'),
    ]
)
def loginprocess(loginbtn, useremail, password, 
                 currentuserid, pathname):    
    ctx = callback_context
    if ctx.triggered:
        accesstype = 0
        alert_open = False 
        alert_color = ""
        alert_text = ""

        eventid = ctx.triggered[0]['prop_id'].split('.')[0] 
        
        if eventid == 'login_loginbtn':
            if loginbtn and useremail and password:
                sql = """
                SELECT user_id, user_access_type
                FROM maindashboard.users
                WHERE
                    user_email = %s AND
                    user_password = %s
                """
                            
                encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest()
                values = [useremail, encrypt_string(password)]
                cols = ['user_id', 'user_access_type']

                # Assuming db.querydatafromdatabase returns a DataFrame
                df = db.querydatafromdatabase(sql, values, cols)
                if df.shape[0]:
                    currentuserid = df['user_id'][0]
                    accesstype = df['user_access_type'][0] 
                    pathname = '/homepage'
                else:
                    currentuserid = -1
                    alert_color = 'danger'
                    alert_text = 'Incorrect username or password.'
                    alert_open = True
            
        return [alert_color, alert_text, alert_open, currentuserid, accesstype, pathname]  # Returning the current URL pathname if login fails
    else:
        raise PreventUpdate
    



@app.callback(
    Output('login_password', 'type'),
    [Input('show_password', 'value')]
)
def toggle_password_visibility(checked_values):
    if checked_values:
        return 'text'
    else:
        return 'password'