async def main() -> None:
    from app.supplier.google_sheets_supplier import gs  # noqa // imported for initilazing
    from app.configs.bot import dp, bot

    from app.routes.start_router import start_router
    from app.routes.main_menu import router as main_menu_router
    from app.routes.back import router as back_router
    from app.routes.change_localization import router as localization_router
    from app.routes.balance import router as balance_router
    from app.routes.cancel import router as cancel_router
    from app.routes.services import router as services_router
    from app.routes.subscription import router as subscription_router
    from app.routes.admin import router as admin_router

    dp.include_router(cancel_router)
    dp.include_router(start_router)
    dp.include_router(main_menu_router)
    dp.include_router(back_router)
    dp.include_router(localization_router)
    dp.include_router(balance_router)
    dp.include_router(services_router)
    dp.include_router(subscription_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)
