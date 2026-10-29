from django.urls import path

from . import views

urlpatterns = [
    path('', views.mainPage, name='mainPage'),

    # скачивание документов
    path('download/', views.download_file, name='download_file'),

    # Вкладки на сайте
    # Юридические страницы
    path('privacy-policy', views.privacyPolicy, name='privacy-policy'),
    path('terms-of-use', views.termsOfUse, name='terms-of-use'),
    path('cookie-policy', views.cookiePolicy, name='cookie-policy'),
    path('refund-policy', views.refundPolicy, name='refund-policy'),

    # Компания

    # О компании
    path('company/aboutCompany', views.aboutCompany, name='company/aboutCompany'),

    # Реквизиты
    path('company/details', views.companyDetails, name='company/details'),

    # Корзина
    path('shopping-cart', views.shoppingCart, name='shopping-cart'),
    path("add-to-cart", views.add_to_cart, name="add_to_cart"),
    path("update-cart/", views.update_cart, name="update_cart"),
    path("place-order/", views.placeOrder, name="place-order"),
    path('request-success/', views.request_success, name='request-success'),

    # Каталог
    # Сварочные аппараты

    path('catalog/welding-machines', views.weldingMachines, name='welding-machines'),

    # Гидравлические 
    path('catalog/welding-machines/hydraulic', views.hydraulicMachines, name='hydraulic'),

    # Механические
    path('catalog/welding-machines/mechanical', views.mechanicalMachines, name='mechanical'),
    
    # Электромуфтовые
    path('catalog/welding-machines/electrofusion', views.electrofusionMachines, name='electrofusion'),
    
    # Раструбные
    path('catalog/welding-machines/bell-shaped', views.bellShapedMachines, name='bell-shaped'),
    

    # Комплектующие

    path('catalog/welding-machines/components', views.componentsMachines, name='components'),
    
    # Электорцеватель
    path('catalog/welding-machines/components/electorate', views.electorate, name='electorate'),

    # Электронагреватель
    path('catalog/welding-machines/components/electricHeater', views.electricHeater, name='electricHeater'),

    # Вкладыши
    path('catalog/welding-machines/components/earbuds', views.earbuds, name='earbuds'),

    # Сканер
    path('catalog/welding-machines/components/scanner', views.scanner, name='scanner'),

    # Центраторы для сварки труб
    path('catalog/welding-machines/components/centralizersPipeWelding', views.centralizersPipeWelding, name='centralizersPipeWelding'),


    # Дополнительные
    
    path('catalog/welding-machines/additional', views.additionalMachines, name='additional'),
    
    # Блок автоматизации
    path('catalog/welding-machines/additional/automationUnit', views.automationUnit, name='automationUnit'),


    # Фитинги

    path('catalog/fitting', views.fitting, name='fitting'),

    # Электросварные фитинги
    path('catalog/fitting/electrofusionFittings', views.electrofusionFittings, name='electrofusionFittings'),

    # Литые фитинги
    path('catalog/fitting/castFittings', views.castFittings, name='castFittings'),


    # Трубы ПНД

    path('catalog/pipes', views.pipes, name='pipes'),

    # Трубы ПНД водопроводные
    path('catalog/pipes/plumbing', views.waterPipes, name='pipes/plumbing'),

    # Трубы ПНД для газа
    path('catalog/pipes/gas', views.gasPipes, name='pipes/gas'),


    # Запорная арматура

    path('catalog/shut-off-valves', views.shutOffValves, name='shut-off-valves'),

    # Фланец
    path('catalog/shut-off-valves/flange', views.shutOffValvesFlange, name='shut-off-valves/flange'),

    # Фланцевые адаптеры
    path('catalog/shut-off-valves/flange-adapters', views.shutOffValvesFlangeAdapters, name='shut-off-valves/flange-adapters'),


    # Услуги
    # Аренда
    path('service/welding-equipment/rental', views.rentalWeldingEquipment, name='rental-welding-equipment'),

    # Ремонт
    path('service/welding-equipment/repair', views.repairWeldingEquipment, name='repair-welding-equipment'),
    
    # Монтаж трубопровода
    path('service/pipeline-installation', views.pipelineInstallation, name='pipeline-installation'),

    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]