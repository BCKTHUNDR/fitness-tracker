from js import window


async def initialize():
    value = await window.getCounterFromDB()
    await window.setCounterInDB(value)


async def get_counter():
    return int(await window.getCounterFromDB())


async def change_counter(amount):
    current = await get_counter()
    new_value = current + amount

    await window.setCounterInDB(new_value)
