#!/usr/bin/python

# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

import json
import os
import random
import uuid
import logging

from locust import HttpUser, task, between
from locust_plugins.users.playwright import PlaywrightUser, pw, PageWithRetry, event

from opentelemetry import context, baggage, trace
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.jinja2 import Jinja2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

from openfeature import api
from openfeature.contrib.provider.flagd import FlagdProvider
from openfeature.contrib.hook.opentelemetry import TracingHook

from playwright.async_api import Route, Request

# logger_provider = LoggerProvider(resource=Resource.create(
#         {
#             "service.name": "load-generator",
#         }
#     ),)
# set_logger_provider(logger_provider)

# exporter = OTLPLogExporter(insecure=True)
# logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
# handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

# # Attach OTLP handler to locust logger
# logging.getLogger().addHandler(handler)
# logging.getLogger().setLevel(logging.INFO)

# exporter = OTLPMetricExporter(insecure=True)
# set_meter_provider(MeterProvider([PeriodicExportingMetricReader(exporter)]))

# tracer_provider = TracerProvider()
# trace.set_tracer_provider(tracer_provider)
# tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

# # Instrumenting manually to avoid error with locust gevent monkey
# Jinja2Instrumentor().instrument()
# RequestsInstrumentor().instrument()
# SystemMetricsInstrumentor().instrument()
# URLLib3Instrumentor().instrument()
# logging.info("Instrumentation complete")

products = [
    "99",   # Adventurer GPS Watch
    "95",   # AeroLite Cycling Helmet
    "88",   # Alpine AlpinePack Backpack
    "3",    # Alpine Fusion Goggles
    "28",   # Alpine Peak Down Jacket
    "18",   # Alpine Tech Crampons
    "17",   # Apex Climbing Harness
    "74",   # Apex Climbing Harness
    "49",   # Arctic Shield Insulated Jacket
]

auth_users = [
    {"username": "alice", "password": "Pass123$", },
    {"username": "bob", "password": "Pass123$", },
]

people_file = open('people.json')
people = json.load(people_file)

# class WebsiteUser(HttpUser):
#     wait_time = between(1, 10)

#     @task
#     def place_order_flow(self):
#         self.login()
#         # self.add_products_to_cart()
#         # self.place_order()
    
    
#     def login(self):
#         print("calling login")
#         response = self.client.post("/signin-oidc", json=auth_user)
#         print("text: ", response.text)
#         print("status code: ", response.status_code)
#         print("headers: ", response.headers)


        
#     # @task(10)
#     # def browse_product(self):
#     #     self.client.get("/item/" + random.choice(products))

#     # @task(3)
#     # def view_cart_and_checkout(self):
#     #     self.client.get("/cart")

#     # @task(2)
#     # def add_to_cart(self, user=""):
#     #     if user == "":
#     #         user = str(uuid.uuid1())
#     #     product = random.choice(products)
#     #     self.client.get("/api/products/" + product)
#     #     cart_item = {
#     #         "item": {
#     #             "productId": product,
#     #             "quantity": random.choice([1, 2, 3, 4, 5, 10]),
#     #         },
#     #         "userId": user,
#     #     }
#     #     self.client.post("/api/cart", json=cart_item)

#     # @task(1)
#     # def checkout(self):
#     #     # checkout call with an item added to cart
#     #     user = str(uuid.uuid1())
#     #     self.add_to_cart(user=user)
#     #     checkout_person = random.choice(people)
#     #     checkout_person["userId"] = user
#     #     self.client.post("/api/checkout", json=checkout_person)

#     # @task(1)
#     # def checkout_multi(self):
#     #     # checkout call which adds 2-4 different items to cart before checkout
#     #     user = str(uuid.uuid1())
#     #     for i in range(random.choice([2, 3, 4])):
#     #         self.add_to_cart(user=user)
#     #     checkout_person = random.choice(people)
#     #     checkout_person["userId"] = user
#     #     self.client.post("/api/checkout", json=checkout_person)

#     def on_start(self):
#         self.place_order_flow()

BASE_URL = "https://localhost:7298/"

class WebsiteBrowserUser(PlaywrightUser):
    wait_time = between(1, 10)
    headless = True  # to use a headless browser, without a GUI
    user_count = 0

    @task
    @pw
    async def place_order_flow(self, page: PageWithRetry):
        print("place_order_flow")
        self.user_id = self.user_count
        self.user_count += 1
        await self.login(page)
        await self.add_products_to_cart()
        await self.place_order()
        

    async def login(self, page: PageWithRetry):
        print("login start")
        await page.goto(f"{BASE_URL}user/login?returnUrl=")
        await page.fill("#Username", auth_users[self.user_id % 2]["username"])
        await page.fill("#Password", auth_users[self.user_id % 2]["password"])
        await page.click('button[value="login"]')
        await page.wait_for_load_state("networkidle")
        print("login ended")

    async def add_products_to_cart(self):
        print("add_products_to_cart start")
        num_products = random.randint(1, 4)
        for _ in range(num_products):
            random_product = random.choice(products)
            await self.page.goto(f"{BASE_URL}item/{random_product}")
            await self.page.click('button[type="submit"][title="Add to basket"]')
            await self.page.wait_for_load_state("networkidle")
        print("add_products_to_cart ended")


    async def place_order(self):
        await self.page.goto(f"{BASE_URL}checkout")
        person = random.choice(people)
        print("place_order start")
        await self.page.fill('input[name="Info.Street"]', person["address"])
        await self.page.fill('input[name="Info.City"]', person["city"])
        await self.page.fill('input[name="Info.State"]', person["state"])
        await self.page.fill('input[name="Info.ZipCode"]', person["zip"])
        await self.page.fill('input[name="Info.Country"]', person["country"])
        await self.page.keyboard.press("Enter")
        await self.page.wait_for_load_state("networkidle")
        print("place_order ended")
    


# async def add_baggage_header(route: Route, request: Request):
#     existing_baggage = request.headers.get('baggage', '')
#     headers = {
#         **request.headers,
#         'baggage': ', '.join(filter(None, (existing_baggage, 'synthetic_request=true')))
#     }
#     await route.continue_(headers=headers)
