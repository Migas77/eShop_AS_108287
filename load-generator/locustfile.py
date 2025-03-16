#!/usr/bin/python

# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

import json
import random
from locust import task, between
from locust_plugins.users.playwright import PlaywrightUser, pw, PageWithRetry

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

BASE_URL = "https://localhost:7298/"

class WebsiteBrowserUser(PlaywrightUser):
    wait_time = between(1, 10)
    headless = True  # to use a headless browser, without a GUI
    user_count = 0

    @task
    @pw
    async def place_order_flow(self, page: PageWithRetry):
        print("place_order_flow")
        self.user_id = WebsiteBrowserUser.user_count
        WebsiteBrowserUser.user_count += 1
        await self.login(page)
        await self.add_products_to_cart()
        await self.place_order()
        

    async def login(self, page: PageWithRetry):
        user = auth_users[self.user_id % 2]
        print(f"login start; id: {id(self)}; username: {user['username']}")
        await page.goto(f"{BASE_URL}user/login?returnUrl=")
        await page.fill("#Username", user["username"])
        await page.fill("#Password", user["password"])
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
    

