def global_context(request):
    """Global context processor for site-wide variables"""
    try:
        company_info = CompanyInfo.objects.first()
    except (ProgrammingError, OperationalError):
        company_info = None
    
    main_categories = []
    try:
        main_categories = Category.objects.filter(is_active=True)[:5]
    except (ProgrammingError, OperationalError):
        pass
    
    return {
        'company_info': company_info,
        'main_categories': main_categories,
        'site_name': company_info.name if company_info else 'Eyedentity Eyewear',
        'site_tagline': company_info.tagline if company_info else 'Stylish. Protective. Uniquely You.',
    }