#!/usr/bin/python

import gevent.monkey

# patch the modules for asynchronous work
gevent.monkey.patch_all()

import time
import threading
import click
import pymavlink.mavutil as utility
import gevent.pywsgi
import flask

# create a flask application
application = flask.Flask(import_name="pymavrest")

# global variables
message_data = {}
message_enumeration = {}
parameter_data = {}
parameter_count_total = 0
parameter_count = set()
plan_data = []
plan_count_total = 0
plan_count = set()


# get all messages
@application.route(rule="/get/message/all", methods=["GET"])
def get_message_all():
    # get all messages
    global message_data

    # expose the response
    return flask.jsonify(message_data)


# get a message by name
@application.route(rule="/get/message/<string:message_name>", methods=["GET"])
def get_message_with_name(message_name):
    # get all messages
    global message_data

    # check if the message is received
    if message_name in message_data.keys():

        # expose the message
        result = message_data[message_name]

    # message not received yet
    else:

        # create empty response
        result = {}

    # expose the response
    return flask.jsonify(result)


# get a message by id
@application.route(rule="/get/message/<int:message_id>", methods=["GET"])
def get_message_with_id(message_id):
    # get all messages and message id numbers
    global message_data, message_enumeration

    # check if the there is a message with requested id
    if message_id in message_enumeration.values():

        # get message name with message id
        message_name = list(message_enumeration.keys())[list(message_enumeration.values()).index(message_id)]

        # check if the message is received
        if message_name in message_data.keys():

            # expose the message
            result = message_data[message_name]

        # message not received yet
        else:

            # create empty response
            result = {}

    # there is no message with requested id
    else:

        # create empty response
        result = {}

    # expose the response
    return flask.jsonify(result)


# get a field of a message with message name
@application.route(rule="/get/message/<string:message_name>/<string:field_name>", methods=["GET"])
def get_message_field_with_name(message_name, field_name):
    # get all messages
    global message_data

    # check if the message is received
    if message_name in message_data.keys():

        # check if the message has the requested field name
        if field_name in message_data[message_name].keys():

            # expose the field name and field value
            result = {field_name: message_data[message_name][field_name]}

        # message does not have the requested field name
        else:

            # create empty response
            result = {}

    # message not received yet
    else:

        # create empty response
        result = {}

    # expose the response
    return flask.jsonify(result)


# get a field of a message with message id
@application.route(rule="/get/message/<int:message_id>/<string:field_name>", methods=["GET"])
def get_message_field_with_id(message_id, field_name):
    # get all messages and message id numbers
    global message_data, message_enumeration

    # check if the there is a message with requested id
    if message_id in message_enumeration.values():

        # get message name with message id
        message_name = list(message_enumeration.keys())[list(message_enumeration.values()).index(message_id)]

        # check if the message is received
        if message_name in message_data.keys():

            # check if the message has the requested field name
            if field_name in message_data[message_name].keys():

                # expose the field name and field value
                result = {field_name: message_data[message_name][field_name]}

            # message does not have the requested field name
            else:

                # create empty response
                result = {}

        # message not received yet
        else:

            # create empty response
            result = {}

    # there is no message with requested id
    else:

        # create empty response
        result = {}

    # expose the response
    return flask.jsonify(result)


# get all parameters
@application.route(rule="/get/parameter/all", methods=["GET"])
def get_parameter_all():
    # get all parameters
    global parameter_data

    # expose the response
    return flask.jsonify(parameter_data)


# get a parameter by name
@application.route(rule="/get/parameter/<string:parameter_name>", methods=["GET"])
def get_parameter_with_name(parameter_name):
    # get all parameters
    global parameter_data

    # check if the parameter is received
    if parameter_name in parameter_data.keys():

        # expose the parameter name and value
        result = {parameter_name: parameter_data[parameter_name]}

    # parameter not received yet
    else:

        # create empty response
        result = {}

    # expose the response
    return flask.jsonify(result)


# get all flight plan
@application.route(rule="/get/plan/all", methods=["GET"])
def get_plan_all():
    # get entire plan
    global plan_data

    # expose the response
    return flask.jsonify(plan_data)


# get a flight plan command by index
@application.route(rule="/get/plan/<int:plan_index>", methods=["GET"])
def get_plan_with_index(plan_index):
    # get entire plan
    global plan_data

    # create empty response
    result = {}

    # find the requested flight plan command by index
    for mission_item in plan_data:
        if mission_item["seq"] == plan_index:
            result = mission_item
            break

    # expose the response
    return flask.jsonify(result)


# deal with the malicious requests
@application.errorhandler(code_or_exception=404)
def page_not_found(error):
    # expose an empty response
    return flask.jsonify({})


# connect to vehicle and parse messages
def receive_telemetry(master, timeout, drop, white, black, param, plan):
    # get global variables
    global message_data, message_enumeration
    global parameter_data, parameter_count_total, parameter_count
    global plan_data, plan_count_total, plan_count

    # zero time out means do not time out
    if timeout == 0:
        timeout = None

    # zero drop means do not drop non-periodic messages
    if drop == 0:
        drop = None

    # create white list set used in non-periodic parameter and flight plan related messages
    white_list = {"PARAM_VALUE", "MISSION_COUNT", "MISSION_ITEM_INT", "MISSION_ACK"}

    # parse white list based on user requirements
    white_list = white_list if white == "" else white_list | {x for x in white.split(",")}

    # parse black list based on user requirements
    black_list = set() if black == "" else {x for x in black.split(",")}

    # user did not request to populate parameter values
    if not param:
        # add parameter value message to black list
        black_list |= {"PARAM_VALUE"}

    # user did not request to populate flight plan items
    if not plan:
        # add flight plan related messages to black list
        black_list |= {"MISSION_COUNT", "MISSION_ITEM_INT", "MISSION_ACK"}

    # infinite connection loop
    while True:

        # connect to vehicle
        vehicle = utility.mavlink_connection(device=master)

        # user requested to populate parameter list or flight plan
        if param or plan:
            # wait until vehicle connection is assured
            vehicle.wait_heartbeat()

        # user requested to populate parameter list
        if param:
            # request parameter list from vehicle
            vehicle.mav.param_request_list_send(vehicle.target_system, vehicle.target_component)

        # user requested to populate flight plan
        if plan:
            # request flight plan from vehicle
            vehicle.mav.mission_request_list_send(vehicle.target_system, vehicle.target_component)

        # infinite message parsing loop
        while True:

            # wait a message from vehicle until specified timeout
            message_raw = vehicle.recv_match(blocking=True, timeout=timeout)

            # do not proceed to message parsing if no message received from vehicle within specified time
            if not message_raw:
                break

            # convert raw message to dictionary
            message_dict = message_raw.to_dict()

            # get and pop message name from message dictionary
            message_name = message_dict.pop("mavpackettype")

            # do not proceed if message is in the black list
            if message_name in black_list:
                continue

            # do not proceed if message is not in the white list
            if len(white) > 1 and message_name not in white_list:
                continue

            # get timestamps
            time_monotonic = time.monotonic()
            time_now = time.time()

            # message contains a parameter value
            if message_name == "PARAM_VALUE":

                # create a parameter space to parameter data if not exist
                if message_dict["param_id"] not in parameter_data.keys():
                    parameter_data[message_dict["param_id"]] = {}

                # get the parameter value
                parameter_data[message_dict["param_id"]]["value"] = message_dict["param_value"]

                # update total parameter count
                parameter_count_total = message_dict["param_count"]

                # add parameter index to parameter count list to not request this parameter value again
                parameter_count.add(message_dict["param_index"])

                # this parameter is populated for the first time
                if "statistics" not in parameter_data[message_dict["param_id"]].keys():

                    # initiate statistics data for this parameter
                    parameter_data[message_dict["param_id"]]["statistics"] = {}
                    parameter_data[message_dict["param_id"]]["statistics"]["counter"] = 1
                    parameter_data[message_dict["param_id"]]["statistics"]["latency"] = 0
                    parameter_data[message_dict["param_id"]]["statistics"]["first"] = time_now
                    parameter_data[message_dict["param_id"]]["statistics"]["first_monotonic"] = time_monotonic
                    parameter_data[message_dict["param_id"]]["statistics"]["last"] = time_now
                    parameter_data[message_dict["param_id"]]["statistics"]["last_monotonic"] = time_monotonic
                    parameter_data[message_dict["param_id"]]["statistics"]["duration"] = 0
                    parameter_data[message_dict["param_id"]]["statistics"]["instant_frequency"] = 0
                    parameter_data[message_dict["param_id"]]["statistics"]["average_frequency"] = 0

                # this parameter was populated before
                else:

                    # update statistics data for this parameter
                    latency = time_monotonic - parameter_data[message_dict["param_id"]]["statistics"]["last_monotonic"]
                    first_monotonic = parameter_data[message_dict["param_id"]]["statistics"]["first_monotonic"]
                    duration = time_monotonic - first_monotonic
                    instant_frequency = 1.0 / latency if latency != 0.0 else 0.0
                    counter = parameter_data[message_dict["param_id"]]["statistics"]["counter"]
                    average_frequency = counter / duration if duration != 0.0 else 0.0
                    parameter_data[message_dict["param_id"]]["statistics"]["counter"] += 1
                    parameter_data[message_dict["param_id"]]["statistics"]["latency"] = latency
                    parameter_data[message_dict["param_id"]]["statistics"]["last"] = time_now
                    parameter_data[message_dict["param_id"]]["statistics"]["last_monotonic"] = time_monotonic
                    parameter_data[message_dict["param_id"]]["statistics"]["duration"] = duration
                    parameter_data[message_dict["param_id"]]["statistics"]["instant_frequency"] = instant_frequency
                    parameter_data[message_dict["param_id"]]["statistics"]["average_frequency"] = average_frequency

                # do not proceed further
                continue

            # there are still unpopulated parameter values so request them
            if param and parameter_count_total != len(parameter_data):
                for i in range(parameter_count_total):
                    if i not in parameter_count:
                        vehicle.mav.param_request_read_send(vehicle.target_system, vehicle.target_component, b"", i)
                        break

            # message means flight plan on the vehicle has changed
            if message_name == "MISSION_ACK":

                # check mission plan is accepted and this acknowledgement is for flight plan
                if message_dict["type"] == 0 and message_dict["mission_type"] == 0:
                    # clear flight plan related variables
                    plan_data = []
                    plan_count = set()
                    plan_count_total = 0

                    # request total flight plan command count
                    vehicle.mav.mission_request_list_send(vehicle.target_system, vehicle.target_component)

                # do not proceed further
                continue

            # message contains total flight plan items on the vehicle
            if message_name == "MISSION_COUNT":

                # check this count is for flight plan
                if message_dict["mission_type"] == 0:
                    # update total flight plan command count
                    plan_count_total = message_dict["count"]

                    # request first flight plan command from vehicle
                    vehicle.mav.mission_request_int_send(vehicle.target_system, vehicle.target_component, 0)

                # do not proceed further
                continue

            # message contains a flight plan item
            if message_name == "MISSION_ITEM_INT":

                # check this flight plan command was not populated before
                if message_dict["seq"] not in plan_count:

                    # initiate statistics data for this flight plan command
                    message_dict["statistics"] = {}
                    message_dict["statistics"]["counter"] = 1
                    message_dict["statistics"]["latency"] = 0
                    message_dict["statistics"]["first"] = time_now
                    message_dict["statistics"]["first_monotonic"] = time_monotonic
                    message_dict["statistics"]["last"] = time_now
                    message_dict["statistics"]["last_monotonic"] = time_monotonic
                    message_dict["statistics"]["duration"] = 0
                    message_dict["statistics"]["instant_frequency"] = 0
                    message_dict["statistics"]["average_frequency"] = 0

                    # add flight plan command to plan data
                    plan_data.append(message_dict)

                    # add flight plan command to plan count list to no request this again
                    plan_count.add(message_dict["seq"])

                    # request the next flight plan commands if there are any
                    if message_dict["seq"] < plan_count_total - 1:
                        seq = message_dict["seq"] + 1
                        vehicle.mav.mission_request_int_send(vehicle.target_system, vehicle.target_component, seq)

                # do not proceed further
                continue

            # there are still unpopulated flight plan commands so request them
            if plan and plan_count_total != len(plan_count):
                for i in range(plan_count_total):
                    if i not in plan_count:
                        vehicle.mav.mission_request_int_send(vehicle.target_system, vehicle.target_component, i)
                        break

            # create a message field in message data if this ordinary message not populated before
            if message_name not in message_data.keys():
                message_data[message_name] = {}

            # update message fields with new fetched data
            message_data[message_name] = {**message_data[message_name], **message_dict}

            # get message id of this message
            message_id = message_raw.get_msgId()

            # add message id of this message to message enumeration list
            message_enumeration[message_name] = message_id

            # this message is populated for the first time
            if "statistics" not in message_data[message_name].keys():

                # initiate statistics data for this message
                message_data[message_name]["statistics"] = {}
                message_data[message_name]["statistics"]["counter"] = 1
                message_data[message_name]["statistics"]["latency"] = 0
                message_data[message_name]["statistics"]["first"] = time_now
                message_data[message_name]["statistics"]["first_monotonic"] = time_monotonic
                message_data[message_name]["statistics"]["last"] = time_now
                message_data[message_name]["statistics"]["last_monotonic"] = time_monotonic
                message_data[message_name]["statistics"]["duration"] = 0
                message_data[message_name]["statistics"]["instant_frequency"] = 0
                message_data[message_name]["statistics"]["average_frequency"] = 0

            # this message was populated before
            else:

                # update statistics data for this message
                latency = time_monotonic - message_data[message_name]["statistics"]["last_monotonic"]
                first_monotonic = message_data[message_name]["statistics"]["first_monotonic"]
                duration = time_monotonic - first_monotonic
                instant_frequency = 1.0 / latency if latency != 0.0 else 0.0
                counter = message_data[message_name]["statistics"]["counter"]
                average_frequency = counter / duration if duration != 0.0 else 0
                message_data[message_name]["statistics"]["counter"] += 1
                message_data[message_name]["statistics"]["latency"] = latency
                message_data[message_name]["statistics"]["last"] = time_now
                message_data[message_name]["statistics"]["last_monotonic"] = time_monotonic
                message_data[message_name]["statistics"]["duration"] = duration
                message_data[message_name]["statistics"]["instant_frequency"] = instant_frequency
                message_data[message_name]["statistics"]["average_frequency"] = average_frequency

            # drop non-periodic messages if user requested
            if drop:
                for message_name in list(message_data.keys()):
                    if time_monotonic - message_data[message_name]["statistics"]["last_monotonic"] > drop:
                        message_data.pop(message_name)


@click.command()
@click.option("--host", default="127.0.0.1", type=click.STRING, required=False,
              help="Pymavrest server IP address.")
@click.option("--port", default=2609, type=click.IntRange(min=0, max=65535), required=False,
              help="Pymavrest server port number.")
@click.option("--master", default="udpin:127.0.0.1:14550", type=click.STRING, required=False,
              help="Standard MAVLink connection string.")
@click.option("--timeout", default=5.0, type=click.FloatRange(min=0, clamp=True), required=False,
              help="Try to reconnect after this seconds when no message is received, zero means do not reconnect")
@click.option("--drop", default=5.0, type=click.FloatRange(min=0, clamp=True), required=False,
              help="Drop non-periodic messages after this seconds, zero means do not drop.")
@click.option("--white", default="", type=click.STRING, required=False,
              help="Comma separated white list to filter messages, empty means all messages are in white list.")
@click.option("--black", default="", type=click.STRING, required=False,
              help="Comma separated black list to filter messages.")
@click.option("--param", default=True, type=click.BOOL, required=False,
              help="Fetch parameters.")
@click.option("--plan", default=True, type=click.BOOL, required=False,
              help="Fetch plan.")
def main(host, port, master, timeout, drop, white, black, param, plan):
    # start telemetry receiver thread
    threading.Thread(target=receive_telemetry, args=(master, timeout, drop, white, black, param, plan)).start()

    # create server
    server = gevent.pywsgi.WSGIServer(listener=(host, port), application=application, log=application.logger)

    # run server
    server.serve_forever()


# main entry point
if __name__ == "__main__":
    # run main function
    main()
