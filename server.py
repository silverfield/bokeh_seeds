from flask import Flask, render_template, request

from bokeh.embed import autoload_server

import atexit
import threading

flask_app = Flask(__name__)
bokeh_thread = None

@atexit.register
def kill_bokeh():
    bokeh_thread.stop()


@flask_app.after_request
def add_header(r):  #this is just to prevent caching of JS code
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


# --- flask routes -----------------------------------------------------------


@flask_app.route('/component')
def nresults_div():
    id = request.args.get('id')
    payload = request.args.to_dict()

    if SELECTED_RES_INDEX in payload:
        payload[SELECTED_RES_INDEX] = int(payload[SELECTED_RES_INDEX])
    if SELECTED_BAR_INDEX in payload:
        payload[SELECTED_BAR_INDEX] = int(payload[SELECTED_BAR_INDEX])
    if CS_ONLY in payload:
        payload[CS_ONLY] = payload[CS_ONLY] == 'true'

    comp = None

    if id == 'nresults-div':
        comp = Presentation.get_nresults_div(payload)
    if id == 'res-table':
        comp = Presentation.get_res_table(payload)
    if id == 'bar-chart':
        comp = Presentation.get_bar_chart(payload)
    if id == 'heatmap':
        comp = Presentation.get_heatmap(payload)
    if id == 'comp-div':
        comp = Presentation.get_comp_div(payload)

    return bh.get_code(comp)


@flask_app.route('/qcompare')
def qcompare():
    uuid_x = request.args.get(SELECTED_HM_X)
    uuid_y = request.args.get(SELECTED_HM_Y)
    sim_class_name = request.args.get(SIM)
    sim_class = all_sims.get_sim_class_by_name(sim_class_name)

    qx = Model.base_df.loc[uuid_x]
    qy = Model.base_df.loc[uuid_y]

    comp_df = simeval.create_comp_df(qx, qy, def_sim=sim_class())
    comp_div = simeval.get_comp_div(comp_df, width=PAGE_WIDTH)

    return render_template('frame.html', content=bh.get_code(comp_div))


@flask_app.route('/simeval')
def simevalroute():
    script = autoload_server(model=None, url="http://localhost:5006/")
    return render_template('frame.html', content=script)



@flask_app.route('/')
def index():
    html = render_template('qexplore.html')
    return render_template('frame.html', content=html)

if __name__ == '__main__':
    bokeh_thread = threading.Thread(target=run_app, kwargs={'show': False})
    bokeh_thread.start()

    print('Opening Flask application on http://localhost:5000/')
    flask_app.run(port=5000)  # With debug=True, Flask server will auto-reload when there are code changes
