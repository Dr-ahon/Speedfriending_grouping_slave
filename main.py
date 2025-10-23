import pandas as pd
from collections import deque
from io import BytesIO
from nicegui import ui, events, native
import sys

# last_name_q = 'Name and surname 🪪'
# type_q = 'What’s your MBTI type?💡'

# ---------- STATE ----------

upload_finished = False
df_form = None
df_app = None
# print(sys.argv[0])

# ---------- HEADER ----------

header_label = ui.label('MBTI group-making slave')
header_label.style('color: #6E93D6; '
                   'font-size: 200%; '
                   'font-size: 26px; '
                   'font-weight: bold')
header_label.classes('mb-8')

# ---------- INPUTS ----------

name_label_text = 'Question on name in the form'
approx_width = max(200, len(name_label_text) * 8)
name_question_input = ((ui.input(label=name_label_text,
                                 placeholder='start typing'))
                       .style(f'width: {approx_width}px;'))

type_label_text = 'Question on MBTI type in the form'
approx_width = max(200, len(type_label_text) * 8)
type_question_input = ((ui.input(label=type_label_text,
                                 placeholder='start typing')
                        .style(f'width: {approx_width}px;'))
                       .classes('mb-3'))

email_label_text = 'Question on email in the form'
approx_width = max(200, len(type_label_text) * 8)
email_question_input = ((ui.input(label=email_label_text,
                                  placeholder='start typing')
                         .style(f'width: {approx_width}px;'))
                        .classes('mb-3'))

grouping_dropdown = ((ui.select(['choose grouping mode', 'balanced roles', 'same roles', 'balanced temperament'],
                                value='choose grouping mode',
                                on_change=lambda e: dropdown_click(e))
                      .style('color: #66666; '
                             'font-size: 120%; '))
                     .classes('mb-4'))


def dropdown_click(e):
    match e.value:
        case 'balanced roles' | 'balanced temperament':
            slider_label.visible = True
            slider.visible = True
        case 'choose grouping mode' | 'same roles':
            slider_label.visible = False
            slider.visible = False


slider_init_value = 5
slider_label = (ui.label(f'Number of groups: {slider_init_value}')
                .style('color: #666666; '
                       'font-size: 120%; '))
slider_label.visible = False

slider = ui.slider(min=0, max=10, value=slider_init_value, on_change=lambda: slider_refresh())
slider.visible = False


def slider_refresh():
    slider_label.set_text(f'Number of groups: {slider.value}')


# ---------- UPLOAD ----------

def upload_form_action(e: events.UploadEventArguments):
    global upload_finished, df_form
    upload_finished = True
    raw = getattr(e.file, '_data', None)
    df_form = pd.read_excel(BytesIO(raw))


def upload_app_action(e: events.UploadEventArguments):
    global upload_finished, df_app
    upload_finished = True
    raw = getattr(e.file, '_data', None)
    df_app = pd.read_excel(BytesIO(raw))


with ui.card():
    ui.label('Upload form answer sheet').style('color: #666666; '
                                               'font-size: 120%; ')

    ui.label('First go see the form results, and then choose save as .xlsx')
    ui.upload(on_upload=upload_form_action, auto_upload=True)

with ui.card():
    ui.label('Upload attendance list').style('color: #666666; '
                                             'font-size: 120%; ')
    ui.label('Go to \'run event \' in ESN app, copy the whole Participant '
             'overview, paste it to excel, and delete first four rows and the first column, ')
    ui.upload(on_upload=upload_app_action, auto_upload=True)

# ---------- ACTIONS ----------

error_label = ui.label().style('color: #E53935; '
                               'font-size: 120%; ')


def on_clic_run():
    error_label.text = ''
    if not upload_finished or df_form is None:
        error_label.text = 'Please upload the XLSX first.'
    elif not name_question_input.value or not type_question_input.value or not email_question_input.value:
        error_label.text = 'Please fill in all column headers.'
    elif (name_question_input.value not in df_form.columns
          or type_question_input.value not in df_form.columns
          or email_question_input.value not in df_form.columns):
        error_label.text = f'Column(s) \'{name_question_input.value}\' not found. Existing: {list(df_form.columns)}'
    elif grouping_dropdown.value == 'choose grouping mode':
        error_label.text = 'Please choose a grouping mode.'
    else:
        compute_groups()


with ui.row().classes('items-left gap-2'):
    run_button = ui.button('RUN', on_click=lambda: on_clic_run())
    run_button.classes('mb-8')

results_container = ui.column().classes('gap-1')


def compute_groups():
    global df_form
    results_container.clear()
    num_groups = slider.value
    name_q = name_question_input.value
    type_q = type_question_input.value
    email_q = email_question_input.value
    df_form = get_present(email_q)
    print('compute_groups')
    print(len(df_form))
    print(df_form)
    type_names = set(df_form[type_q].dropna())
    mode = grouping_dropdown.value

    match mode:
        case 'balanced roles':
            grouped_people = group_people_by_role(name_q, type_q, type_names)

            deq_of_lists = deque([[] for _ in range(num_groups)])

            for type_name, (typed_people_list, t) in grouped_people.items():
                for person in typed_people_list:
                    deq_of_lists[0].append((person, type_name))
                    deq_of_lists.rotate(1)

        case 'same roles':
            grouped_people = group_people_by_role(name_q, type_q, type_names)
            deq_of_lists = deque([])

            for type_name, (typed_people_list, t) in grouped_people.items():
                deq_of_lists.appendleft([])

                for person in typed_people_list:
                    deq_of_lists[0].append((person, type_name))

        case 'balanced temperament':
            grouped_people = group_people_by_temperament(name_q, type_q, type_names)

            deq_of_lists = deque([[] for _ in range(num_groups)])

            for type_name, (typed_people_list, t) in grouped_people.items():
                for person in typed_people_list:
                    deq_of_lists[0].append((person, type_name))
                    deq_of_lists.rotate(1)

    with results_container:
        for i in range(len(deq_of_lists)):

            group_label = ui.label(f'Group {i + 1}')
            group_label.style('color: #666666; '
                              'font-size: 120%; '
                              'margin-top: 20px; ')

            for person_info in deq_of_lists[i]:
                person_label = ui.label(f'{person_info[1]}   {person_info[0]}').style(
                    'margin-left: 40px; color: #333333; font-size: 18px;')


def get_present(email_q):
    global df_form, df_app
    df_form[email_q] = df_form[email_q].astype(str).str.strip()
    df_app['Email'] = df_app['E-mail'].astype(str).str.strip()
    df_app = df_app[df_app['Check in'].notna()]
    print(len(df_app['Check in']))
    print(len(df_app['E-mail']))
    x = df_form[df_form[email_q].isin(df_app['E-mail'])]
    print(len(x))
    return x


def group_people_by_role(last_name_q, type_q, type_names):
    role_map = {
        'SP': [t for t in type_names if t[1] == 'S' and t[3] == 'P'],
        'NT': [t for t in type_names if t[1] == 'N' and t[2] == 'T'],
        'NF': [t for t in type_names if t[1] == 'N' and t[2] == 'F'],
        'SJ': [t for t in type_names if t[1] == 'S' and t[3] == 'J']
    }
    type_to_role = {t: role for role, lst in role_map.items() for t in lst}
    order = ['SP', 'NT', 'NF', 'SJ']
    sorted_types = sorted(type_names, key=lambda t: order.index(type_to_role.get(t)))
    g = {type: (df_form.loc[df_form[type_q] == type][last_name_q].dropna(), type) for type in sorted_types}
    return g


def group_people_by_temperament(last_name_q, type_q, type_names):
    temperament_map = {
        'I': [t for t in type_names if t[0] == 'I'],
        'E': [t for t in type_names if t[0] == 'E']
    }
    type_to_role = {t: role for role, lst in temperament_map.items() for t in lst}
    order = ['E', 'I']
    sorted_types = sorted(type_names, key=lambda t: order.index(type_to_role.get(t)))
    g = {type: (df_form.loc[df_form[type_q] == type][last_name_q].dropna(), type) for type in sorted_types}
    return g


ui.run(reload=False, port=native.find_open_port())
