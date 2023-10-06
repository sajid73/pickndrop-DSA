
from flask import Flask, request, jsonify
from flask_cors import CORS  


app = Flask(__name__)
CORS(app)  

def calculate(employees, vehicles):
  '''
  employees: a dictionary containing details of employees location and time
             i.e. {'udoy':
                          {
                            'zone': 'north',
                            'arrival': '10 AM'
                           }
                  }
  vehicles: a dictionary containing details of every avaiable vehcile with its capacity
            i.e. {'vahicle 1':
                                {
                                  'capacity': 4
                                }
                  }
  '''
  zones = ['north', 'south', 'east', 'west', 'central']
  int_to_zones = {k: v for k, v in enumerate(zones)}
  zones_to_int = {v: k for k, v in enumerate(zones)}
  time_matrix = [[0 for _ in range(5)] for _ in range(5)]

  # north to other position
  time_matrix[0][1] = 180
  time_matrix[0][2] = 120
  time_matrix[0][3] = 60
  time_matrix[0][4] = 40

  # south to other position
  time_matrix[1][0] = 180
  time_matrix[1][2] = 110
  time_matrix[1][3] = 90
  time_matrix[1][4] = 50

  # east to other position
  time_matrix[2][0] = 100
  time_matrix[2][1] = 120
  time_matrix[2][3] = 150
  time_matrix[2][4] = 20

  # west to other position
  time_matrix[3][0] = 70
  time_matrix[3][1] = 79
  time_matrix[3][2] = 130
  time_matrix[3][4] = 40

  # central to other position
  time_matrix[4][0] = 30
  time_matrix[4][1] = 42
  time_matrix[4][2] = 25
  time_matrix[4][3] = 40

  # initializing zones for vehicles
  for v in vehicles:
    vehicles[v]['zone'] = []
    vehicles[v]['assigned_employee'] = []

  arrival_time = []
  assigned_vehicles_to_employee_by_time = {}
  init_vehicles = vehicles
  final_vehicle_list_by_time = {}

  # getting unique arrival times
  for id, e in enumerate(employees):
    arrival_time.append(employees[e]['arrival'])

  arrival_time = list(set(arrival_time))
  # print(arrival_time)

  for time in arrival_time:
    employees_grouped_by_time = [e for _, e in enumerate(employees) if employees[e]['arrival'] == time]
    assigned_vehicles_to_employee = {}
    for e in employees_grouped_by_time:
       assigned_vehicles_to_employee[e] = ''

    if len(employees_grouped_by_time) == 0:
      continue

    for zone in zones:
      employees_grouped_by_time_and_zone = [e for e in employees_grouped_by_time if employees[e]['zone'] == zone]

      if len(employees_grouped_by_time_and_zone) == 0:
        continue

      for e in employees_grouped_by_time_and_zone:
        for v in vehicles:
          if len(vehicles[v]['zone']) == 0 or zone in vehicles[v]['zone']:
            if vehicles[v]['capacity'] > 0:
              if len(vehicles[v]['zone']) == 0:
                vehicles[v]['zone'].append(zone)
              vehicles[v]['assigned_employee'].append(e)
              vehicles[v]['capacity'] -= 1
              assigned_vehicles_to_employee[e] = v
              break

      for e in employees_grouped_by_time_and_zone:
        # print(e)
        if assigned_vehicles_to_employee[e] == '':
          # print(f'check --> {e}')
          destination_zone = zones_to_int[employees[e]['zone']]
          selected_vehicle = None
          req_min_time = 24*60
          for v in vehicles:
            if vehicles[v]['capacity'] > 0:
              current_zone = zones_to_int[vehicles[v]['zone'][-1]]
              req_time = time_matrix[current_zone][destination_zone] + time_matrix[destination_zone][zones_to_int['central']]
              if req_min_time > req_time:
                req_min_time = req_time
                selected_vehicle = v

          assigned_vehicles_to_employee[e] = selected_vehicle
          vehicles[selected_vehicle]['zone'].append(employees[e]['zone'])
          vehicles[selected_vehicle]['assigned_employee'].append(e)
          vehicles[selected_vehicle]['capacity'] -= 1

    assigned_vehicles_to_employee_by_time[time] = assigned_vehicles_to_employee
    final_vehicle_list_by_time[time] = vehicles
    vehicles = init_vehicles

  return assigned_vehicles_to_employee_by_time, final_vehicle_list_by_time

@app.route('/', methods=['GET'])
def api_welcome():
  return "Welcome to pickndrop\nGo to \calculate and POST method to calculate result"

@app.route('/calculate', methods=['POST'])
def api_calculate():
    try:

        data = request.json
        employees = data['employees']
        vehicles = data['vehicles']


        result = calculate(employees, vehicles)
        
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)