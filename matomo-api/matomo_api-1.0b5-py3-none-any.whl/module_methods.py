"""
This module is generated at Fri 21-May-2021 15:53h from the Matomo API
documentation at https://developer.matomo.org/api-reference/reporting-api, the
Report Metadata as requested via API.getReportMetadata, the Metrics glossary as
requested via API.getGlossaryMetrics and as documented at
https://glossary.matomo.org/.
"""

from requests import Response
from .parameter_specifications import QryDict
from .decorators import module_decorator, method_decorator


class MatomoApi:
    """
    Reporting API Reference

    This is the Matomo API Reference. It lists all functions that can be called,
    documents the parameters, and links to examples for every call in the
    various formats.

    The APIs let you programmatically request any analytics reports from Matomo,
    for one or several websites and for any given date and period and in any
    format (CSV, JSON, XML, etc.). Matomo also provides Management APIs to
    create, update and delete websites, users, user privileges, custom
    dashboards, email reports, goals, funnels, custom dimensions, alerts,
    videos, heatmaps, session recordings, custom segments, and more.
    """
    def __init__(self, url='https://demo.matomo.cloud', token='anonymous'):
        self._url = url
        self._token = token
    
    def API(self):
        """
        This API is the Metadata API: it gives information about all other
        available APIs methods, as well as providing human readable and more
        complete outputs than normal API methods. Some of the information that
        is returned by the Metadata API:

        - the dynamically generated list of all API methods via
          "getReportMetadata"

        - the list of metrics that will be returned by each method, along with
          their human readable name, via "getDefaultMetrics" and
          "getDefaultProcessedMetrics"

        - the list of segments metadata supported by all functions that have a
          'segment' parameter

        - the (truly magic) method "getProcessedReport" will return a human
          readable version of any other report, and include the processed
          metrics such as conversion rate, time on site, etc. which are not
          directly available in other methods.

        - the method "getSuggestedValuesForSegment" returns top suggested values
          for a particular segment. It uses the Live.getLastVisitsDetails API to
          fetch the most recently used values, and will return the most often
          used values first.

        The Metadata API is for example used by the Matomo Mobile App to
        automatically display all Matomo reports, with translated report &
        columns names and nicely formatted values. More information on the
        Metadata API documentation page
        """
        return ModAPI(self._url, self._token)
    
    def AbTesting(self):
        """
        This API module is not documented.
        """
        return ModAbTesting(self._url, self._token)
    
    def Actions(self):
        """
        The Actions API lets you request reports for all your Visitor Actions:
        Page URLs, Page titles, Events, Content Tracking, File Downloads and
        Clicks on external websites. For example, "getPageTitles" will return
        all your page titles along with standard Actions metrics for each row.
        It is also possible to request data for a specific Page Title with
        "getPageTitle" and setting the parameter pageName to the page title you
        wish to request. Similarly, you can request metrics for a given Page URL
        via "getPageUrl", a Download file via "getDownload" and an outlink via
        "getOutlink". Note: pageName, pageUrl, outlinkUrl, downloadUrl
        parameters must be URL encoded before you call the API.
        """
        return ModActions(self._url, self._token)
    
    def ActivityLog(self):
        """
        The Activity Log API is used to get the activity logs for users in your
        Matomo instance.

        The method ActivityLog.getEntries returns a list of the activities done
        by users in your Matomo instance.

        The list of activities returned depends on which user is calling the
        API:

        - if you authenticate with a Super User access, the API will return
          activity logs for all users

        - if you authenticate as anonymous (no authentication), or a user with
          view or admin access, only this user's activity will be returned.

        Each activity includes an activity ID, the user who initiated the
        activity, a list of parameters/metadata specific to this activity, the
        datetime (and pretty datetime), the activity description, and the URL to
        the colored avatar image for this user.

        The activity log includes over 80 different types of Matomo activities,
        for example:

        - See when a user logged in, failed to log in, or logged out

        - See when a user was created, updated or deleted by who

        - See when a website was created, updated or deleted by who

        - See when a Matomo setting, an A/B Test, a Scheduled Report, or a
          Segment was changed and by who
        """
        return ModActivityLog(self._url, self._token)
    
    def Annotations(self):
        """
        API for annotations plugin. Provides methods to create, modify, delete &
        query annotations.
        """
        return ModAnnotations(self._url, self._token)
    
    def Contents(self):
        """
        API for plugin Contents
        """
        return ModContents(self._url, self._token)
    
    def CoreAdminHome(self):
        """
        This API module is not documented.
        """
        return ModCoreAdminHome(self._url, self._token)
    
    def CustomAlerts(self):
        """
        This API module is not documented.
        """
        return ModCustomAlerts(self._url, self._token)
    
    def CustomDimensions(self):
        """
        The Custom Dimensions API lets you manage and access reports for your
        configured Custom Dimensions.
        """
        return ModCustomDimensions(self._url, self._token)
    
    def CustomJsTracker(self):
        """
        API for plugin CustomJsTracke
        """
        return ModCustomJsTracker(self._url, self._token)
    
    def CustomReports(self):
        """
        The Custom Reports API lets you 1) create custom reports within Matomo
        and 2) view the created reports in the Matomo Reporting UI or consume
        them via the API.

        You can choose between different visualizations (eg table or evolution
        graph) and combine hundreds of dimensions and metrics to get the data
        you need.
        """
        return ModCustomReports(self._url, self._token)
    
    def CustomVariables(self):
        """
        The Custom Variables API lets you access reports for your Custom
        Variables names and values.
        """
        return ModCustomVariables(self._url, self._token)
    
    def Dashboard(self):
        """
        This API is the Dashboard API: it gives information about dashboards.
        """
        return ModDashboard(self._url, self._token)
    
    def DevicePlugins(self):
        """
        The DevicePlugins API lets you access reports about device plugins such
        as browser plugins.
        """
        return ModDevicePlugins(self._url, self._token)
    
    def DevicesDetection(self):
        """
        The DevicesDetection API lets you access reports on your visitors
        devices, brands, models, Operating system, Browsers.
        """
        return ModDevicesDetection(self._url, self._token)
    
    def Events(self):
        """
        The Events API lets you request reports about your users' Custom Events.
        Events are tracked using the Javascript Tracker trackEvent() function,
        or using the [Tracking HTTP
        API](http://developer.matomo.org/api-reference/tracking-api).

        An event is defined by an event category (Videos, Music, Games...), an
        event action (Play, Pause, Duration, Add Playlist, Downloaded,
        Clicked...), and an optional event name (a movie name, a song title,
        etc.) and an optional numeric value.

        This API exposes the following Custom Events reports: getCategory lists
        the top Event Categories, getAction lists the top Event Actions, getName
        lists the top Event Names.

        These Events report define the following metrics: nb_uniq_visitors,
        nb_visits, nb_events. If you define values for your events, you can
        expect to see the following metrics: nb_events_with_value,
        sum_event_value, min_event_value, max_event_value, avg_event_value

        The Events.get* reports can be used with an optional &secondaryDimension
        parameter. Secondary dimension is the dimension used in the sub-table of
        the Event report you are requesting.

        Here are the possible values of secondaryDimension:

        - For Events.getCategory you can set secondaryDimension to eventAction
          or eventName.

        - For Events.getAction you can set secondaryDimension to eventName or
          eventCategory.

        - For Events.getName you can set secondaryDimension to eventAction or
          eventCategory.

        For example, to request all Custom Events Categories, and for each, the
        top Event actions, you would request:
        method=Events.getCategory&secondaryDimension=eventAction&flat=1. You may
        also omit &flat=1 in which case, to get top Event actions for one Event
        category, use method=Events.getActionFromCategoryId passing it the
        &idSubtable= of this Event category.
        """
        return ModEvents(self._url, self._token)
    
    def Feedback(self):
        """
        API for plugin Feedback
        """
        return ModFeedback(self._url, self._token)
    
    def FormAnalytics(self):
        """
        The Form Analytics API lets you 1) manage forms within Matomo and 2)
        request all your form analytics reports and metrics.

        1) You can create, update, delete forms, as well as request any form and
        also archive them.

        2) Request all metrics and reports about how users interact with your
        forms:

        - Form usage by page URL to see whether the same form is used
          differently on different pages.

        - Entry fields to see where they start filling out your forms.

        - Drop off fields to see where your users leave your forms.

        - Field timings report to see where your users spent the most time.

        - Field size report to see how much text your users type.

        - Most corrected fields report to learn more about where users have
          problems filling out your form.

        - Unneeded fields report to see which fields are often left blank.

        - Several evolution reports of all metrics to see how your forms perform
          over time.

        And the following metrics:

        - How often was a form field interacted with (eg. focus or change).

        - Which fields did your visitors interact with first when they started
          filling out a form.

        - Which fields caused a visitor to stop filling out a form (drop offs).

        - How often your visitors changed a form field or made amendments.

        - How often a field was refocused or corrected (eg usage of backspace or
          delete key, cursor keys, …).

        - How much text they type into each of your text fields.

        - Which fields are unneeded and often left blank.

        - How long visitors hesitated (waited) before they started changing a
          field.

        - How much time your visitors spent on each field.
        """
        return ModFormAnalytics(self._url, self._token)
    
    def Funnels(self):
        """
        API for plugin Funnels
        """
        return ModFunnels(self._url, self._token)
    
    def Goals(self):
        """
        Goals API lets you Manage existing goals, via "updateGoal" and
        "deleteGoal", create new Goals via "addGoal", or list existing Goals for
        one or several websites via "getGoals" If you are tracking Ecommerce
        orders and products on your site, the functions "getItemsSku",
        "getItemsName" and "getItemsCategory" will return the list of products
        purchased on your site, either grouped by Product SKU, Product Name or
        Product Category. For each name, SKU or category, the following metrics
        are returned: Total revenue, Total quantity, average price, average
        quantity, number of orders (or abandoned carts) containing this product,
        number of visits on the Product page, Conversion rate. By default, these
        functions return the 'Products purchased'. These functions also accept
        an optional parameter &abandonedCarts=1. If the parameter is set, it
        will instead return the metrics for products that were left in an
        abandoned cart therefore not purchased. The API also lets you request
        overall Goal metrics via the method "get": Conversions, Visits with at
        least one conversion, Conversion rate and Revenue. If you wish to
        request specific metrics about Ecommerce goals, you can set the
        parameter &idGoal=ecommerceAbandonedCart to get metrics about abandoned
        carts (including Lost revenue, and number of items left in the cart) or
        &idGoal=ecommerceOrder to get metrics about Ecommerce orders (number of
        orders, visits with an order, subtotal, tax, shipping, discount,
        revenue, items ordered) See also the documentation about Tracking Goals
        in Matomo.
        """
        return ModGoals(self._url, self._token)
    
    def HeatmapSessionRecording(self):
        """
        API for plugin Heatmap & Session Recording. When you request activity
        data for a heatmap or a recorded session, please note that any X or Y
        coordinate, scroll reach position, and above the fold is relative and
        not absolute. X and Y coordinate are between 0 and 2000 and are relative
        to the selector where 2000 means the position is at 100% of the element,
        1000 means the position is at 50% and 0 means the position is actually 0
        pixel from the element. Scroll and above the fold positions are between
        0 and 1000. If for example a web page is 3000 pixel high, and scroll
        reach is 100, it means the user has seen the content up to 300 pixels
        (10%, or 100 of 1000). We differentiate between two different IDs here:
        idSiteHsr represents the ID of a heatmap or session recording
        configuration idLogHsr represents the ID of an actually recorded /
        tracked session or heatmap activity
        """
        return ModHeatmapSessionRecording(self._url, self._token)
    
    def ImageGraph(self):
        """
        The ImageGraph.get API call lets you generate beautiful static PNG
        Graphs for any existing Matomo report. Supported graph types are: line
        plot, 2D/3D pie chart and vertical bar chart. A few notes about some of
        the parameters available:

        - $graphType defines the type of graph plotted, accepted values are:
          'evolution', 'verticalBar', 'pie' and '3dPie'

        - $colors accepts a comma delimited list of colors that will overwrite
          the default Matomo colors

        - you can also customize the width, height, font size, metric being
          plotted (in case the data contains multiple columns/metrics). See also
          How to embed static Image Graphs? for more information.
        """
        return ModImageGraph(self._url, self._token)
    
    def Insights(self):
        """
        API for plugin Insights
        """
        return ModInsights(self._url, self._token)
    
    def LanguagesManager(self):
        """
        The LanguagesManager API lets you access existing Matomo translations,
        and change Users languages preferences. "getTranslationsForLanguage"
        will return all translation strings for a given language, so you can
        leverage Matomo translations in your application (and automatically
        benefit from the 40+ translations!). This is mostly useful to developers
        who integrate Matomo API results in their own application. You can also
        request the default language to load for a user via
        "getLanguageForUser", or update it via "setLanguageForUser".
        """
        return ModLanguagesManager(self._url, self._token)
    
    def Live(self):
        """
        The Live! API lets you access complete visit level information about
        your visitors. Combined with the power of Segmentation, you will be able
        to request visits filtered by any criteria. The method
        "getLastVisitsDetails" will return extensive data for each visit, which
        includes: server time, visitId, visitorId, visitorType (new or
        returning), number of pages, list of all pages (and events, file
        downloaded and outlinks clicked), custom variables names and values set
        to this visit, number of goal conversions (and list of all Goal
        conversions for this visit, with time of conversion, revenue, URL,
        etc.), but also other attributes such as: days since last visit, days
        since first visit, country, continent, visitor IP, provider, referrer
        used (referrer name, keyword if it was a search engine, full URL),
        campaign name and keyword, operating system, browser, type of screen,
        resolution, supported browser plugins (flash, java, silverlight, pdf,
        etc.), various dates & times format to make it easier for API users...
        and more! With the parameter '&segment=' you can filter the returned
        visits by any criteria (visitor IP, visitor ID, country, keyword used,
        time of day, etc.). The method "getCounters" is used to return a simple
        counter: visits, number of actions, number of converted visits, in the
        last N minutes. See also the documentation about Real time widget and
        visitor level reports in Matomo.
        """
        return ModLive(self._url, self._token)
    
    def Login(self):
        """
        API for plugin Login
        """
        return ModLogin(self._url, self._token)
    
    def MarketingCampaignsReporting(self):
        """
        API for plugin MarketingCampaignsReporting
        """
        return ModMarketingCampaignsReporting(self._url, self._token)
    
    def MediaAnalytics(self):
        """
        The MediaAnalytics API lets you request your reports about how your
        Video and Audio are accessed and viewed on your websites and apps. Some
        of the methods return Real Time information (similarly to the Live!
        API), while others return all your videos and audios and their key
        metrics.

        The real time methods can return information about the last N minutes
        (or last N hours). They include the following:

        - the method getCurrentNumPlays returns the number of video plays (and
          audio plays) in the last N minutes

        - the method getCurrentSumTimeSpent returns the the total time users
          spent playing your media in the last N minutes

        - the method getCurrentMostPlays returns the most popular videos in the
          last N minutes.

        The other methods return the aggregated analytics reports for Video and
        Audio:

        - MediaAnalytics.get returns the overall metrics for your videos and
          audios: nb_plays, nb_unique_visitors_plays, nb_impressions,
          nb_unique_visitors_impressions, nb_finishes, sum_total_time_watched,
          sum_total_audio_plays, sum_total_audio_impressions,
          sum_total_video_plays, sum_total_video_impressions, play_rate,
          finish_rate, impression_rate.

        - getVideoTitles and getAudioTitles return the list of videos / audio by
          video title and audio title.

        - getGroupedVideoResources and getGroupedAudioResources return the list
          of watched videos / audio grouped by resource URL. The "grouped media
          resource" report displays a flat report which includes both the domain
          and the path to the media resource, whereas the regular "media
          resource" report displays a hierarchical view of your media resources
          by domain.

        - getVideoHours and getAudioHours return the list of videos / audio by
          by hour (to see how your media is consumed at a different time of the
          day).

        - getVideoTitles and getAudioTitles return the list of videos / audio by
          video title and audio title.

        - getVideoResolutions return the list of videos by player resolution
          (see how your videos are consumed when the video resolution varies).

        - getPlayers return the watched media by media player.
        """
        return ModMediaAnalytics(self._url, self._token)
    
    def MobileMessaging(self):
        """
        The MobileMessaging API lets you manage and access all the
        MobileMessaging plugin features including : - manage SMS API credential
        - activate phone numbers - check remaining credits - send SMS
        """
        return ModMobileMessaging(self._url, self._token)
    
    def MultiChannelConversionAttribution(self):
        """
        Multi Channel Conversion Attribution API
        """
        return ModMultiChannelConversionAttribution(self._url, self._token)
    
    def MultiSites(self):
        """
        The MultiSites API lets you request the key metrics (visits, page views,
        revenue) for all Websites in Matomo.
        """
        return ModMultiSites(self._url, self._token)
    
    def Overlay(self):
        """
        Class API
        """
        return ModOverlay(self._url, self._token)
    
    def PagePerformance(self):
        """
        This API module is not documented.
        """
        return ModPagePerformance(self._url, self._token)
    
    def PrivacyManager(self):
        """
        API for plugin PrivacyManage
        """
        return ModPrivacyManager(self._url, self._token)
    
    def Referrers(self):
        """
        The Referrers API lets you access reports about Websites, Search
        engines, Keywords, Campaigns used to access your website. For example,
        "getKeywords" returns all search engine keywords (with general analytics
        metrics for each keyword), "getWebsites" returns referrer websites
        (along with the full Referrer URL if the parameter &expanded=1 is set).
        "getReferrerType" returns the Referrer overview report. "getCampaigns"
        returns the list of all campaigns (and all campaign keywords if the
        parameter &expanded=1 is set).
        """
        return ModReferrers(self._url, self._token)
    
    def Resolution(self):
        """
        This API module is not documented.
        """
        return ModResolution(self._url, self._token)
    
    def RollUpReporting(self):
        """
        API for plugin RollUpReporting
        """
        return ModRollUpReporting(self._url, self._token)
    
    def SEO(self):
        """
        The SEO API lets you access a list of SEO metrics for the specified URL:
        Google PageRank, Google/Bing indexed pages Alexa Rank and age of the
        Domain name.
        """
        return ModSEO(self._url, self._token)
    
    def ScheduledReports(self):
        """
        The ScheduledReports API lets you manage Scheduled Email reports, as
        well as generate, download or email any existing report.
        "generateReport" will generate the requested report (for a specific date
        range, website and in the requested language). "sendEmailReport" will
        send the report by email to the recipients specified for this report.
        You can also get the list of all existing reports via "getReports",
        create new reports via "addReport", or manage existing reports with
        "updateReport" and "deleteReport". See also the documentation about
        Scheduled Email reports in Matomo.
        """
        return ModScheduledReports(self._url, self._token)
    
    def SearchEngineKeywordsPerformance(self):
        """
        The SearchEngineKeywordsPerformance API lets you download all your SEO
        search keywords from Google, Bing & Yahoo and Yandex, as well as getting
        a detailed overview of how search robots crawl your websites and any
        error they may encounter.

        1) download all your search keywords as they were searched on Google,
        Bing & Yahoo and Yandex. This includes Google Images, Google Videos and
        Google News. This lets you view all keywords normally hidden from view
        behind "keyword not defined". With this plugin you can view them all!

        2) download all crawling overview stats and metrics from Bring and Yahoo
        and Google. Many metrics are available such as: Crawled pages, Crawl
        errors, Connection timeouts, HTTP-Status Code 301 (Permanently moved),
        HTTP-Status Code 400-499 (Request errors), All other HTTP-Status Codes,
        Total pages in index, Robots.txt exclusion, DNS failures, HTTP-Status
        Code 200-299, HTTP-Status Code 301 (Temporarily moved), HTTP-Status Code
        500-599 (Internal server errors), Malware infected sites, Total inbound
        links. \Plugins\SearchEngineKeywordsPerformance
        """
        return ModSearchEngineKeywordsPerformance(self._url, self._token)
    
    def SegmentEditor(self):
        """
        The SegmentEditor API lets you add, update, delete custom Segments, and
        list saved segments.
        """
        return ModSegmentEditor(self._url, self._token)
    
    def SitesManager(self):
        """
        The SitesManager API gives you full control on Websites in Matomo
        (create, update and delete), and many methods to retrieve websites based
        on various attributes. This API lets you create websites via "addSite",
        update existing websites via "updateSite" and delete websites via
        "deleteSite". When creating websites, it can be useful to access
        internal codes used by Matomo for currencies via "getCurrencyList", or
        timezones via "getTimezonesList". There are also many ways to request a
        list of websites: from the website ID via "getSiteFromId" or the site
        URL via "getSitesIdFromSiteUrl". Often, the most useful technique is to
        list all websites that are known to a current user, based on the
        token_auth, via "getSitesWithAdminAccess", "getSitesWithViewAccess" or
        "getSitesWithAtLeastViewAccess" (which returns both). Some methods will
        affect all websites globally: "setGlobalExcludedIps" will set the list
        of IPs to be excluded on all websites,
        "setGlobalExcludedQueryParameters" will set the list of URL parameters
        to remove from URLs for all websites. The existing values can be fetched
        via "getExcludedIpsGlobal" and "getExcludedQueryParametersGlobal". See
        also the documentation about Managing Websites in Matomo.
        """
        return ModSitesManager(self._url, self._token)
    
    def TagManager(self):
        """
        API for plugin Tag Manager. Lets you configure all your containers,
        create, update and delete tags, triggers, and variables. Create and
        publish new releases, enable and disable preview/debug mode, and much
        more. Please note: A container may have several versions. The current
        version that a user is editing is called the "draft" version. You can
        get the ID of the "draft" version by calling {@link
        TagManager.getContainer}.
        """
        return ModTagManager(self._url, self._token)
    
    def Tour(self):
        """
        API for Tour plugin which helps you getting familiar with Matomo.
        """
        return ModTour(self._url, self._token)
    
    def Transitions(self):
        """
        This API module is not documented.
        """
        return ModTransitions(self._url, self._token)
    
    def TwoFactorAuth(self):
        """
        This API module is not documented.
        """
        return ModTwoFactorAuth(self._url, self._token)
    
    def UserCountry(self):
        """
        The UserCountry API lets you access reports about your visitors'
        Countries and Continents.
        """
        return ModUserCountry(self._url, self._token)
    
    def UserId(self):
        """
        API for plugin UserId. Allows to get User IDs table.
        """
        return ModUserId(self._url, self._token)
    
    def UserLanguage(self):
        """
        The UserLanguage API lets you access reports about your Visitors
        language setting
        """
        return ModUserLanguage(self._url, self._token)
    
    def UsersFlow(self):
        """
        API for Users Flow. The API lets you explore details about how your
        users or visitors navigate through your website.
        """
        return ModUsersFlow(self._url, self._token)
    
    def UsersManager(self):
        """
        The UsersManager API lets you Manage Users and their permissions to
        access specific websites. You can create users via "addUser", update
        existing users via "updateUser" and delete users via "deleteUser". There
        are many ways to list users based on their login "getUser" and
        "getUsers", their email "getUserByEmail", or which users have permission
        (view or admin) to access the specified websites
        "getUsersWithSiteAccess". Existing Permissions are listed given a login
        via "getSitesAccessFromUser", or a website ID via
        "getUsersAccessFromSite", or you can list all users and websites for a
        given permission via "getUsersSitesFromAccess". Permissions are set and
        updated via the method "setUserAccess". See also the documentation about
        Managing Users in Matomo.
        """
        return ModUsersManager(self._url, self._token)
    
    def VisitFrequency(self):
        """
        VisitFrequency API lets you access a list of metrics related to
        Returning Visitors.
        """
        return ModVisitFrequency(self._url, self._token)
    
    def VisitTime(self):
        """
        VisitTime API lets you access reports by Hour (Server time), and by Hour
        Local Time of your visitors.
        """
        return ModVisitTime(self._url, self._token)
    
    def VisitorInterest(self):
        """
        VisitorInterest API lets you access two Visitor Engagement reports:
        number of visits per number of pages, and number of visits per visit
        duration.
        """
        return ModVisitorInterest(self._url, self._token)
    
    def VisitsSummary(self):
        """
        VisitsSummary API lets you access the core web analytics metrics
        (visits, unique visitors, count of actions (page views & downloads &
        clicks on outlinks), time on site, bounces and converted visits.
        """
        return ModVisitsSummary(self._url, self._token)
    

@module_decorator
class ModAPI:
    """
    This API is the Metadata API: it gives information about all other available
    APIs methods, as well as providing human readable and more complete outputs
    than normal API methods. Some of the information that is returned by the
    Metadata API:

    - the dynamically generated list of all API methods via "getReportMetadata"

    - the list of metrics that will be returned by each method, along with their
      human readable name, via "getDefaultMetrics" and
      "getDefaultProcessedMetrics"

    - the list of segments metadata supported by all functions that have a
      'segment' parameter

    - the (truly magic) method "getProcessedReport" will return a human readable
      version of any other report, and include the processed metrics such as
      conversion rate, time on site, etc. which are not directly available in
      other methods.

    - the method "getSuggestedValuesForSegment" returns top suggested values for
      a particular segment. It uses the Live.getLastVisitsDetails API to fetch
      the most recently used values, and will return the most often used values
      first.

    The Metadata API is for example used by the Matomo Mobile App to
    automatically display all Matomo reports, with translated report & columns
    names and nicely formatted values. More information on the Metadata API
    documentation page
    """
    pass

    @method_decorator
    def getMatomoVersion(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getMatomoVersion&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getMatomoVersion&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getMatomoVersion&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPhpVersion(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getPhpVersion&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getPhpVersion&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getPhpVersion&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getIpFromHeader(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getIpFromHeader&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getIpFromHeader&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getIpFromHeader&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSettings(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getSettings&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getSettings&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getSettings&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSegmentsMetadata(self, **qry_pars):
        """
        Parameters:

        idSites (cs-list)

        ----------

        Parameter examples:

        - idSites=1,2

        - _hideImplementationData=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getSegmentsMetadata&idSites=1,2&_hideImplementationData=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getSegmentsMetadata&idSites=1,2&_hideImplementationData=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getSegmentsMetadata&idSites=1,2&_hideImplementationData=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getMetadata(self, **qry_pars):
        """
        Parameters:

        idSite / apiModule / apiAction / apiParameters (cs-list) / language /
        period / date / hideMetricsDoc / showSubtableReports

        ----------

        Parameter examples:

        - idSite=1

        - apiModule=UserCountry

        - apiAction=getCountry

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getMetadata&idSite=1&apiModule=UserCountry&apiAction=getCountry&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getMetadata&idSite=1&apiModule=UserCountry&apiAction=getCountry&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getMetadata&idSite=1&apiModule=UserCountry&apiAction=getCountry&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=API.getMetadata&idSite=1&apiModule=UserCountry&apiAction=getCountry&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getReportMetadata(self, **qry_pars):
        """
        Parameters:

        idSites / period / date / hideMetricsDoc / showSubtableReports / idSite

        ----------

        Parameter examples:

        - idSites=1,2

        - period=day

        - date=yesterday / date=last10

        - idSite=1

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getReportMetadata&idSites=1,2&period=day&date=yesterday&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getReportMetadata&idSites=1,2&period=day&date=yesterday&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getReportMetadata&idSites=1,2&period=day&date=yesterday&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=API.getReportMetadata&idSites=1,2&period=day&date=last10&idSite=1&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getProcessedReport(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / apiModule / apiAction / segment / apiParameters
        / idGoal / language / showTimer / hideMetricsDoc / idSubtable /
        showRawMetrics / format_metrics / idDimension

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - apiModule=UserCountry

        - apiAction=getCountry

        - showTimer=1

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getProcessedReport&idSite=1&period=day&date=yesterday&apiModule=UserCountry&apiAction=getCountry&showTimer=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getProcessedReport&idSite=1&period=day&date=yesterday&apiModule=UserCountry&apiAction=getCountry&showTimer=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getProcessedReport&idSite=1&period=day&date=yesterday&apiModule=UserCountry&apiAction=getCountry&showTimer=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=API.getProcessedReport&idSite=1&period=day&date=last10&apiModule=UserCountry&apiAction=getCountry&showTimer=1&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getReportPagesMetadata(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getReportPagesMetadata&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getReportPagesMetadata&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getReportPagesMetadata&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getWidgetMetadata(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getWidgetMetadata&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getWidgetMetadata&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getWidgetMetadata&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def get(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment / columns

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.get&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.get&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.get&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=API.get&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getRowEvolution(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / apiModule / apiAction / label / segment /
        column / language / idGoal / legendAppendMetric / labelUseAbsoluteUrl /
        idDimension / labelSeries

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - apiModule=UserCountry

        - apiAction=getCountry

        - legendAppendMetric=1

        - labelUseAbsoluteUrl=1

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getRowEvolution&idSite=1&period=day&date=yesterday&apiModule=UserCountry&apiAction=getCountry&legendAppendMetric=1&labelUseAbsoluteUrl=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getRowEvolution&idSite=1&period=day&date=yesterday&apiModule=UserCountry&apiAction=getCountry&legendAppendMetric=1&labelUseAbsoluteUrl=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getRowEvolution&idSite=1&period=day&date=yesterday&apiModule=UserCountry&apiAction=getCountry&legendAppendMetric=1&labelUseAbsoluteUrl=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=API.getRowEvolution&idSite=1&period=day&date=last10&apiModule=UserCountry&apiAction=getCountry&legendAppendMetric=1&labelUseAbsoluteUrl=1&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getBulkRequest(self, **qry_pars):
        """
        Parameters:

        urls

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def isPluginActivated(self, **qry_pars):
        """
        Parameters:

        pluginName

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSuggestedValuesForSegment(self, **qry_pars):
        """
        Parameters:

        segmentName / idSite

        ----------

        Parameter examples:

        - segmentName=pageTitle

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getSuggestedValuesForSegment&segmentName=pageTitle&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getSuggestedValuesForSegment&segmentName=pageTitle&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getSuggestedValuesForSegment&segmentName=pageTitle&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPagesComparisonsDisabledFor(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getPagesComparisonsDisabledFor&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getPagesComparisonsDisabledFor&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getPagesComparisonsDisabledFor&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getGlossaryReports(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getGlossaryReports&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getGlossaryReports&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getGlossaryReports&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getGlossaryMetrics(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=API.getGlossaryMetrics&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=API.getGlossaryMetrics&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=API.getGlossaryMetrics&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModAbTesting:
    """
    This API module is not documented.
    """
    pass

    @method_decorator
    def getMetricsOverview(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idExperiment / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getMetricDetails(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idExperiment / successMetric / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addExperiment(self, **qry_pars):
        """
        Parameters:

        idSite / name / hypothesis / description / variations / includedTargets
        / successMetrics

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateExperiment(self, **qry_pars):
        """
        Parameters:

        idExperiment / idSite / name / description / hypothesis / variations /
        confidenceThreshold / mdeRelative / percentageParticipants /
        successMetrics / includedTargets / excludedTargets (cs-list) / startDate
        / endDate

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def startExperiment(self, **qry_pars):
        """
        Parameters:

        idExperiment / idSite

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def finishExperiment(self, **qry_pars):
        """
        Parameters:

        idExperiment / idSite

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def archiveExperiment(self, **qry_pars):
        """
        Parameters:

        idExperiment / idSite

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getJsIncludeTemplate(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getJsIncludeTemplate&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getJsIncludeTemplate&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getJsIncludeTemplate&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getJsExperimentTemplate(self, **qry_pars):
        """
        Parameters:

        idExperiment / idSite

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAllExperiments(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAllExperiments&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAllExperiments&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAllExperiments&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getActiveExperiments(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getActiveExperiments&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getActiveExperiments&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getActiveExperiments&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getExperimentsByStatuses(self, **qry_pars):
        """
        Parameters:

        idSite / statuses

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getExperiment(self, **qry_pars):
        """
        Parameters:

        idExperiment / idSite

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteExperiment(self, **qry_pars):
        """
        Parameters:

        idExperiment / idSite

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableStatuses(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAvailableStatuses&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAvailableStatuses&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAvailableStatuses&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableSuccessMetrics(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAvailableSuccessMetrics&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAvailableSuccessMetrics&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAvailableSuccessMetrics&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableTargetAttributes(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAvailableTargetAttributes&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAvailableTargetAttributes&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getAvailableTargetAttributes&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getExperimentsWithReports(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getExperimentsWithReports&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getExperimentsWithReports&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=AbTesting.getExperimentsWithReports&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModActions:
    """
    The Actions API lets you request reports for all your Visitor Actions: Page
    URLs, Page titles, Events, Content Tracking, File Downloads and Clicks on
    external websites. For example, "getPageTitles" will return all your page
    titles along with standard Actions metrics for each row. It is also possible
    to request data for a specific Page Title with "getPageTitle" and setting
    the parameter pageName to the page title you wish to request. Similarly, you
    can request metrics for a given Page URL via "getPageUrl", a Download file
    via "getDownload" and an outlink via "getOutlink". Note: pageName, pageUrl,
    outlinkUrl, downloadUrl parameters must be URL encoded before you call the
    API.
    """
    pass

    @method_decorator
    def get(self, **qry_pars):
        """
        Actions - Main metrics

        ----------

        This report provides a very basic overview of what actions your visitors
        take on your website.

        (cat: Actions)

        ----------

        Parameters:

        idSite / period / date / segment / columns

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_pageviews: Pageviews

        The number of times this page was visited.

        - nb_uniq_pageviews: Unique Pageviews

        The number of visits that included this page. If a page was viewed
        multiple times during one visit, it is only counted once.

        - nb_downloads: Downloads

        The number of times this link was clicked.

        - nb_uniq_downloads: Unique Downloads

        The number of visits that involved a click on this link. If a link was
        clicked multiple times during one visit, it is only counted once.

        - nb_outlinks: Outlinks

        The number of times this link was clicked.

        - nb_uniq_outlinks: Unique Outlinks

        The number of visits that involved a click on this link. If a link was
        clicked multiple times during one visit, it is only counted once.

        - nb_searches: Searches

        The number of visits that searched for this keyword on your website's
        search engine.

        - nb_keywords: Unique Keywords

        

        - avg_time_generation: Avg. generation time

        The average time it took to generate the page. This metric includes the
        time it took the server to generate the web page, plus the time it took
        for the visitor to download the response from the server. A lower 'Avg.
        generation time' means a faster website for your visitors!

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.get&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.get&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.get&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.get&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPageUrls(self, **qry_pars):
        """
        Page URLs

        ----------

        This report contains information about the page URLs that have been
        visited.

        The table is organized hierarchically, the URLs are displayed as a
        folder structure.

        Use the plus and minus icons on the left to navigate.

        (dim: Page URL / cat: Actions / subcat: Pages)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / idSubtable / depth / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_hits: Pageviews

        The number of times this page was visited.

        - nb_visits: Unique Pageviews

        The number of visits that included this page. If a page was viewed
        multiple times during one visit, it is only counted once.

        - avg_time_on_page: Avg. time on page

        The average amount of time visitors spent on this page (only the page,
        not the entire website).

        - bounce_rate: Bounce Rate

        The percentage of visits that started on this page and left the website
        straight away.

        - exit_rate: Exit rate

        The percentage of visits that left the website after viewing this page.

        - avg_time_generation: Avg. generation time

        The average time it took to generate the page. This metric includes the
        time it took the server to generate the web page, plus the time it took
        for the visitor to download the response from the server. A lower 'Avg.
        generation time' means a faster website for your visitors!

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrls&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrls&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrls&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrls&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPageUrlsFollowingSiteSearch(self, **qry_pars):
        """
        Pages Following a Site Search

        ----------

        When visitors search on your website, they are looking for a particular
        page, content, product, or service. This report lists the pages that
        were clicked the most after an internal search. In other words, the list
        of pages the most searched for by visitors already on your website.

        Use the plus and minus icons on the left to navigate.

        (dim: Destination Page / cat: Actions / subcat: Site Search)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / idSubtable

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_hits_following_search: Clicked in search results

        The number of times this Page was visited after a visitor did a search
        on your website, and clicked on this page in the search results.

        - nb_hits: Pageviews

        The number of times this page was visited.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrlsFollowingSiteSearch&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrlsFollowingSiteSearch&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrlsFollowingSiteSearch&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrlsFollowingSiteSearch&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPageTitlesFollowingSiteSearch(self, **qry_pars):
        """
        Page Titles Following a Site Search

        ----------

        When visitors search on your website, they are looking for a particular
        page, content, product, or service. This report lists the pages that
        were clicked the most after an internal search. In other words, the list
        of pages the most searched for by visitors already on your website.

        Use the plus and minus icons on the left to navigate.

        (dim: Destination Page / cat: Actions / subcat: Site Search)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / idSubtable

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_hits_following_search: Clicked in search results

        The number of times this Page was visited after a visitor did a search
        on your website, and clicked on this page in the search results.

        - nb_hits: Pageviews

        The number of times this page was visited.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageTitlesFollowingSiteSearch&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageTitlesFollowingSiteSearch&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageTitlesFollowingSiteSearch&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageTitlesFollowingSiteSearch&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getEntryPageUrls(self, **qry_pars):
        """
        Entry pages

        ----------

        This report contains information about the entry pages that were used
        during the specified period. An entry page is the first page that a user
        views during their visit.

        The entry URLs are displayed as a folder structure.

        Use the plus and minus icons on the left to navigate.

        (dim: Entry Page URL / cat: Actions / subcat: Entry pages)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / idSubtable / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - entry_nb_visits: Entrances

        Number of visits that started on this page.

        - entry_bounce_count: Bounces

        Number of visits that started and ended on this page. This means that
        the visitor left the website after viewing only this page.

        - bounce_rate: Bounce Rate

        Ratio of visits leaving the website after landing on this page.

        - avg_time_generation: Avg. generation time

        The average time it took to generate the page. This metric includes the
        time it took the server to generate the web page, plus the time it took
        for the visitor to download the response from the server. A lower 'Avg.
        generation time' means a faster website for your visitors!

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getEntryPageUrls&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getEntryPageUrls&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getEntryPageUrls&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getEntryPageUrls&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getExitPageUrls(self, **qry_pars):
        """
        Exit pages

        ----------

        This report contains information about the exit pages that occurred
        during the specified period. An exit page is the last page that a user
        views during their visit.

        The exit URLs are displayed as a folder structure.

        Use the plus and minus icons on the left to navigate.

        (dim: Exit Page URL / cat: Actions / subcat: Exit pages)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / idSubtable / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - exit_nb_visits: Exits

        Number of visits that ended on this page.

        - nb_visits: Unique Pageviews

        The number of visits that included this page. If a page was viewed
        multiple times during one visit, it is only counted once.

        - exit_rate: Exit rate

        The percentage of visits that left the website after viewing this page.

        - avg_time_generation: Avg. generation time

        The average time it took to generate the page. This metric includes the
        time it took the server to generate the web page, plus the time it took
        for the visitor to download the response from the server. A lower 'Avg.
        generation time' means a faster website for your visitors!

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getExitPageUrls&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getExitPageUrls&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getExitPageUrls&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getExitPageUrls&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPageUrl(self, **qry_pars):
        """
        Parameters:

        pageUrl / idSite / period / date / segment

        ----------

        Parameter examples:

        - pageUrl=https://divezone.net/

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrl&pageUrl=https://divezone.net/&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrl&pageUrl=https://divezone.net/&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrl&pageUrl=https://divezone.net/&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageUrl&pageUrl=https://divezone.net/&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPageTitles(self, **qry_pars):
        """
        Page titles

        ----------

        This report contains information about the titles of the pages that have
        been visited.

        The page title is the HTML <title> Tag that most browsers show in their
        window title.

        (dim: Page Title / cat: Actions / subcat: Page titles)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / idSubtable / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_hits: Pageviews

        The number of times this page was visited.

        - nb_visits: Unique Pageviews

        The number of visits that included this page. If a page was viewed
        multiple times during one visit, it is only counted once.

        - avg_time_on_page: Avg. time on page

        The average amount of time visitors spent on this page (only the page,
        not the entire website).

        - bounce_rate: Bounce Rate

        The percentage of visits that started on this page and left the website
        straight away.

        - exit_rate: Exit rate

        The percentage of visits that left the website after viewing this page.

        - avg_time_generation: Avg. generation time

        The average time it took to generate the page. This metric includes the
        time it took the server to generate the web page, plus the time it took
        for the visitor to download the response from the server. A lower 'Avg.
        generation time' means a faster website for your visitors!

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageTitles&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageTitles&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageTitles&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getPageTitles&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getEntryPageTitles(self, **qry_pars):
        """
        Entry page titles

        ----------

        This report contains information about the titles of entry pages that
        were used during the specified period. Use the plus and minus icons on
        the left to navigate.

        (dim: Entry Page title / cat: Actions / subcat: Entry pages)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / idSubtable / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - entry_nb_visits: Entrances

        Number of visits that started on this page.

        - entry_bounce_count: Bounces

        Number of visits that started and ended on this page. This means that
        the visitor left the website after viewing only this page.

        - bounce_rate: Bounce Rate

        The percentage of visits that started on this page and left the website
        straight away.

        - avg_time_generation: Avg. generation time

        The average time it took to generate the page. This metric includes the
        time it took the server to generate the web page, plus the time it took
        for the visitor to download the response from the server. A lower 'Avg.
        generation time' means a faster website for your visitors!

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getEntryPageTitles&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getEntryPageTitles&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getEntryPageTitles&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getEntryPageTitles&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getExitPageTitles(self, **qry_pars):
        """
        Exit page titles

        ----------

        This report contains information about the titles of exit pages that
        occurred during the specified period. Use the plus and minus icons on
        the left to navigate.

        (dim: Exit Page Title / cat: Actions / subcat: Exit pages)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / idSubtable / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - exit_nb_visits: Exits

        Number of visits that ended on this page.

        - nb_visits: Unique Pageviews

        The number of visits that included this page. If a page was viewed
        multiple times during one visit, it is only counted once.

        - exit_rate: Exit rate

        The percentage of visits that left the website after viewing this page.

        - avg_time_generation: Avg. generation time

        The average time it took to generate the page. This metric includes the
        time it took the server to generate the web page, plus the time it took
        for the visitor to download the response from the server. A lower 'Avg.
        generation time' means a faster website for your visitors!

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getExitPageTitles&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getExitPageTitles&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getExitPageTitles&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getExitPageTitles&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPageTitle(self, **qry_pars):
        """
        Parameters:

        pageName / idSite / period / date / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getDownloads(self, **qry_pars):
        """
        Downloads

        ----------

        In this report, you can see which files your visitors have downloaded.

        What Matomo counts as a download is the click on a download link.
        Whether the download was completed or not isn't known to Matomo.

        (dim: Download URL / cat: Actions / subcat: Downloads)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / idSubtable / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Unique Downloads

        The number of visits that involved a click on this link. If a link was
        clicked multiple times during one visit, it is only counted once.

        - nb_hits: Downloads

        The number of times this link was clicked.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getDownloads&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getDownloads&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getDownloads&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getDownloads&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getDownload(self, **qry_pars):
        """
        Parameters:

        downloadUrl / idSite / period / date / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getOutlinks(self, **qry_pars):
        """
        Outlinks

        ----------

        This report shows a hierarchical list of outlink URLs that were clicked
        by your visitors. An outlink is a link that leads the visitor away from
        your website (to another domain).

        Use the plus and minus icons on the left to navigate.

        (dim: Clicked Outlink / cat: Actions / subcat: Outlinks)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / idSubtable / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Unique Clicks

        The number of visits that involved a click on this link. If a link was
        clicked multiple times during one visit, it is only counted once.

        - nb_hits: Clicks

        The number of times this link was clicked.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getOutlinks&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getOutlinks&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getOutlinks&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getOutlinks&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getOutlink(self, **qry_pars):
        """
        Parameters:

        outlinkUrl / idSite / period / date / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSiteSearchKeywords(self, **qry_pars):
        """
        Site Search Keywords

        ----------

        This report lists the Search Keywords that visitors searched for on your
        internal Search Engine.

        Tracking searches that visitors make on your website is a very effective
        way to learn more about what your audience is looking for, it can help
        find ideas for new content, new Ecommerce products that potential
        customers might be searching for, and generally improve the visitors'
        experience on your website.

        (dim: Keyword / cat: Actions / subcat: Site Search)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Searches

        The number of visits that searched for this keyword on your website's
        search engine.

        - nb_pages_per_search: Search Results pages

        Visitors will search on your website, and sometimes click "next" to view
        more results. This is the average number of search results pages viewed
        for this keyword.

        - exit_rate: % Search Exits

        The percentage of visits that left the website after searching for this
        Keyword on your Site Search engine.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchKeywords&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchKeywords&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchKeywords&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchKeywords&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSiteSearchNoResultKeywords(self, **qry_pars):
        """
        Search Keywords with No Results

        ----------

        Tracking searches that visitors make on your website is a very effective
        way to learn more about what your audience is looking for, it can help
        find ideas for new content, new Ecommerce products that potential
        customers might be searching for, and generally improve the visitors'
        experience on your website.

        This report lists the Search Keywords that did not return any Search
        result: maybe the search engine algorithm can be improved, or maybe your
        visitors are looking for content that is not (yet) on your website?

        (dim: Keyword with No Search Result / cat: Actions / subcat: Site
        Search)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Searches

        The number of visits that searched for this keyword on your website's
        search engine.

        - exit_rate: % Search Exits

        The percentage of visits that left the website after searching for this
        Keyword on your Site Search engine.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchNoResultKeywords&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchNoResultKeywords&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchNoResultKeywords&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchNoResultKeywords&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSiteSearchCategories(self, **qry_pars):
        """
        Search Categories

        ----------

        This report lists the Categories that visitors selected when they made a
        Search on your website.

        For example, Ecommerce websites typically have a "Category" selector so
        that visitors can restrict their searches to all products in a specific
        Category.

        (dim: Search Category / cat: Actions / subcat: Site Search)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Searches

        The number of visits that searched for this keyword on your website's
        search engine.

        - nb_pages_per_search: Search Results pages

        Visitors will search on your website, and sometimes click "next" to view
        more results. This is the average number of search results pages viewed
        for this keyword.

        - exit_rate: % Search Exits

        The percentage of visits that left the website after searching for this
        Keyword on your Site Search engine.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchCategories&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchCategories&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchCategories&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Actions.getSiteSearchCategories&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModActivityLog:
    """
    The Activity Log API is used to get the activity logs for users in your
    Matomo instance.

    The method ActivityLog.getEntries returns a list of the activities done by
    users in your Matomo instance.

    The list of activities returned depends on which user is calling the API:

    - if you authenticate with a Super User access, the API will return activity
      logs for all users

    - if you authenticate as anonymous (no authentication), or a user with view
      or admin access, only this user's activity will be returned.

    Each activity includes an activity ID, the user who initiated the activity,
    a list of parameters/metadata specific to this activity, the datetime (and
    pretty datetime), the activity description, and the URL to the colored
    avatar image for this user.

    The activity log includes over 80 different types of Matomo activities, for
    example:

    - See when a user logged in, failed to log in, or logged out

    - See when a user was created, updated or deleted by who

    - See when a website was created, updated or deleted by who

    - See when a Matomo setting, an A/B Test, a Scheduled Report, or a Segment
      was changed and by who
    """
    pass

    @method_decorator
    def getEntries(self, **qry_pars):
        """
        Parameters:

        offset / limit / filterByUserLogin / filterByActivityType

        ----------

        Parameter examples:

        - offset=0

        - limit=25

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=ActivityLog.getEntries&offset=0&limit=25&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=ActivityLog.getEntries&offset=0&limit=25&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=ActivityLog.getEntries&offset=0&limit=25&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getEntryCount(self, **qry_pars):
        """
        Parameters:

        filterByUserLogin / filterByActivityType

        ----------

        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=ActivityLog.getEntryCount&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=ActivityLog.getEntryCount&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=ActivityLog.getEntryCount&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModAnnotations:
    """
    API for annotations plugin. Provides methods to create, modify, delete &
    query annotations.
    """
    pass

    @method_decorator
    def add(self, **qry_pars):
        """
        Parameters:

        idSite / date / note / starred

        ----------

        Parameter examples:

        - starred=0

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def save(self, **qry_pars):
        """
        Parameters:

        idSite / idNote / date / note / starred

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def delete(self, **qry_pars):
        """
        Parameters:

        idSite / idNote

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteAll(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Annotations.deleteAll&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Annotations.deleteAll&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Annotations.deleteAll&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def get(self, **qry_pars):
        """
        Parameters:

        idSite / idNote

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAll(self, **qry_pars):
        """
        Parameters:

        idSite / date / period / lastN

        ----------

        Parameter examples:

        - idSite=1

        - date=yesterday / date=last10

        - period=day

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Annotations.getAll&idSite=1&date=yesterday&period=day&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Annotations.getAll&idSite=1&date=yesterday&period=day&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Annotations.getAll&idSite=1&date=yesterday&period=day&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Annotations.getAll&idSite=1&date=last10&period=day&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAnnotationCountForDates(self, **qry_pars):
        """
        Parameters:

        idSite / date / period / lastN / getAnnotationText

        ----------

        Parameter examples:

        - idSite=1

        - date=yesterday / date=last10

        - period=day

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Annotations.getAnnotationCountForDates&idSite=1&date=yesterday&period=day&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Annotations.getAnnotationCountForDates&idSite=1&date=yesterday&period=day&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Annotations.getAnnotationCountForDates&idSite=1&date=yesterday&period=day&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Annotations.getAnnotationCountForDates&idSite=1&date=last10&period=day&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModContents:
    """
    API for plugin Contents
    """
    pass

    @method_decorator
    def getContentNames(self, **qry_pars):
        """
        Content Name

        ----------

        This report shows the names of the content your visitors viewed and
        interacted with.

        (dim: Content Name / cat: Actions / subcat: Contents)

        ----------

        Parameters:

        idSite / period / date / segment / idSubtable

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_impressions: Impressions

        An impression is counted each time your website is displayed in a search
        engine results page.

        - nb_interactions: Content Interactions

        The number of times a content block was interacted with (eg, a 'click'
        on a banner or ad).

        - interaction_rate: Interaction Rate

        The ratio of content impressions to interactions.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Contents.getContentNames&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Contents.getContentNames&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Contents.getContentNames&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Contents.getContentNames&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContentPieces(self, **qry_pars):
        """
        Content Piece

        ----------

        This report shows the pieces of content your visitors viewed and
        interacted with.

        (dim: Content Piece / cat: Actions / subcat: Contents)

        ----------

        Parameters:

        idSite / period / date / segment / idSubtable

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_impressions: Impressions

        An impression is counted each time your website is displayed in a search
        engine results page.

        - nb_interactions: Content Interactions

        The number of times a content block was interacted with (eg, a 'click'
        on a banner or ad).

        - interaction_rate: Interaction Rate

        The ratio of content impressions to interactions.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Contents.getContentPieces&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Contents.getContentPieces&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Contents.getContentPieces&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Contents.getContentPieces&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModCoreAdminHome:
    """
    This API module is not documented.
    """
    pass

    @method_decorator
    def deleteAllTrackingFailures(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CoreAdminHome.deleteAllTrackingFailures&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CoreAdminHome.deleteAllTrackingFailures&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CoreAdminHome.deleteAllTrackingFailures&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteTrackingFailure(self, **qry_pars):
        """
        Parameters:

        idSite / idFailure

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getTrackingFailures(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CoreAdminHome.getTrackingFailures&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CoreAdminHome.getTrackingFailures&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CoreAdminHome.getTrackingFailures&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModCustomAlerts:
    """
    This API module is not documented.
    """
    pass

    @method_decorator
    def getValuesForAlertInPast(self, **qry_pars):
        """
        Parameters:

        idAlert / subPeriodN

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAlert(self, **qry_pars):
        """
        Parameters:

        idAlert

        ----------

        Parameter examples:

        - idAlert=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.getAlert&idAlert=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.getAlert&idAlert=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.getAlert&idAlert=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAlerts(self, **qry_pars):
        """
        Parameters:

        idSites / ifSuperUserReturnAllAlerts

        ----------

        Parameter examples:

        - idSites=1,2

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.getAlerts&idSites=1,2&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.getAlerts&idSites=1,2&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.getAlerts&idSites=1,2&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addAlert(self, **qry_pars):
        """
        Parameters:

        name / idSites / period / emailMe / additionalEmails / phoneNumbers /
        metric / metricCondition / metricValue / comparedTo / reportUniqueId /
        reportCondition / reportValue

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def editAlert(self, **qry_pars):
        """
        Parameters:

        idAlert / name / idSites / period / emailMe / additionalEmails /
        phoneNumbers / metric / metricCondition / metricValue / comparedTo /
        reportUniqueId / reportCondition / reportValue

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteAlert(self, **qry_pars):
        """
        Parameters:

        idAlert

        ----------

        Parameter examples:

        - idAlert=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.deleteAlert&idAlert=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.deleteAlert&idAlert=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.deleteAlert&idAlert=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getTriggeredAlerts(self, **qry_pars):
        """
        Parameters:

        idSites

        ----------

        Parameter examples:

        - idSites=1,2

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.getTriggeredAlerts&idSites=1,2&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.getTriggeredAlerts&idSites=1,2&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomAlerts.getTriggeredAlerts&idSites=1,2&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModCustomDimensions:
    """
    The Custom Dimensions API lets you manage and access reports for your
    configured Custom Dimensions.
    """
    pass

    @method_decorator
    def getCustomDimension(self, **qry_pars):
        """
        Page Type

        ----------

        (dim: Page Type / cat: Actions / subcat: customdimension5)

        ----------

        Parameters:

        idDimension / idSite / period / date / segment / expanded / flat /
        idSubtable

        ----------

        Metrics:

        - nb_hits: Actions

        The number of times this page was visited.

        - nb_visits: Unique Actions

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - avg_time_on_dimension: Avg. Time On Dimension

        

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - exit_rate: Exit rate

        The percentage of visits that left the website after viewing this page.

        - avg_time_generation: Avg. generation time

        The average time it took to generate the page. This metric includes the
        time it took the server to generate the web page, plus the time it took
        for the visitor to download the response from the server. A lower 'Avg.
        generation time' means a faster website for your visitors!

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def configureNewCustomDimension(self, **qry_pars):
        """
        Parameters:

        idSite / name / scope / active / extractions (cs-list) / caseSensitive

        ----------

        Parameter examples:

        - caseSensitive=1

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def configureExistingCustomDimension(self, **qry_pars):
        """
        Parameters:

        idDimension / idSite / name / active / extractions (cs-list) /
        caseSensitive

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getConfiguredCustomDimensions(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomDimensions.getConfiguredCustomDimensions&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomDimensions.getConfiguredCustomDimensions&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomDimensions.getConfiguredCustomDimensions&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getConfiguredCustomDimensionsHavingScope(self, **qry_pars):
        """
        Parameters:

        idSite / scope

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableScopes(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomDimensions.getAvailableScopes&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomDimensions.getAvailableScopes&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomDimensions.getAvailableScopes&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableExtractionDimensions(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomDimensions.getAvailableExtractionDimensions&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomDimensions.getAvailableExtractionDimensions&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomDimensions.getAvailableExtractionDimensions&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModCustomJsTracker:
    """
    API for plugin CustomJsTracke
    """
    pass

    @method_decorator
    def doesIncludePluginTrackersAutomatically(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomJsTracker.doesIncludePluginTrackersAutomatically&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomJsTracker.doesIncludePluginTrackersAutomatically&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomJsTracker.doesIncludePluginTrackersAutomatically&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModCustomReports:
    """
    The Custom Reports API lets you 1) create custom reports within Matomo and
    2) view the created reports in the Matomo Reporting UI or consume them via
    the API.

    You can choose between different visualizations (eg table or evolution
    graph) and combine hundreds of dimensions and metrics to get the data you
    need.
    """
    pass

    @method_decorator
    def addCustomReport(self, **qry_pars):
        """
        Parameters:

        idSite / name / reportType / metricIds / categoryId / dimensionIds
        (cs-list) / subcategoryId / description / segmentFilter

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateCustomReport(self, **qry_pars):
        """
        Parameters:

        idSite / idCustomReport / name / reportType / metricIds / categoryId /
        dimensionIds (cs-list) / subcategoryId / description / segmentFilter

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getConfiguredReports(self, **qry_pars):
        """
        Parameters:

        idSite / skipCategoryMetadata

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getConfiguredReports&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getConfiguredReports&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getConfiguredReports&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getConfiguredReport(self, **qry_pars):
        """
        Parameters:

        idSite / idCustomReport

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteCustomReport(self, **qry_pars):
        """
        Parameters:

        idSite / idCustomReport

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableCategories(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableCategories&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableCategories&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableCategories&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableReportTypes(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableReportTypes&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableReportTypes&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableReportTypes&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableDimensions(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableDimensions&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableDimensions&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableDimensions&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableMetrics(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableMetrics&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableMetrics&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomReports.getAvailableMetrics&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCustomReport(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idCustomReport / segment / expanded / flat /
        idSubtable / columns

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModCustomVariables:
    """
    The Custom Variables API lets you access reports for your Custom Variables
    names and values.
    """
    pass

    @method_decorator
    def getCustomVariables(self, **qry_pars):
        """
        Custom Variables

        ----------

        This report contains information about your Custom Variables. Click on a
        variable name to see the distribution of the values.

        For more information about Custom Variables in general, read the `Custom
        Variables documentation on matomo.org
        <https://matomo.org/docs/custom-variables/" rel="noreferrer noopener"
        target="_blank>`_

        (dim: Custom Variable name / cat: Visitors / subcat: Custom Variables)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomVariables.getCustomVariables&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomVariables.getCustomVariables&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomVariables.getCustomVariables&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=CustomVariables.getCustomVariables&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCustomVariablesValuesFromNameId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUsagesOfSlots(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=CustomVariables.getUsagesOfSlots&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=CustomVariables.getUsagesOfSlots&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=CustomVariables.getUsagesOfSlots&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModDashboard:
    """
    This API is the Dashboard API: it gives information about dashboards.
    """
    pass

    @method_decorator
    def getDashboards(self, **qry_pars):
        """
        Parameters:

        login / returnDefaultIfEmpty

        ----------

        Parameter examples:

        - login=

        - returnDefaultIfEmpty=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Dashboard.getDashboards&login=&returnDefaultIfEmpty=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Dashboard.getDashboards&login=&returnDefaultIfEmpty=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Dashboard.getDashboards&login=&returnDefaultIfEmpty=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def createNewDashboardForUser(self, **qry_pars):
        """
        Parameters:

        login / dashboardName / addDefaultWidgets

        ----------

        Parameter examples:

        - addDefaultWidgets=1

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def removeDashboard(self, **qry_pars):
        """
        Parameters:

        idDashboard / login

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def copyDashboardToUser(self, **qry_pars):
        """
        Parameters:

        idDashboard / copyToUser / dashboardName

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def resetDashboardLayout(self, **qry_pars):
        """
        Parameters:

        idDashboard / login

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModDevicePlugins:
    """
    The DevicePlugins API lets you access reports about device plugins such as
    browser plugins.
    """
    pass

    @method_decorator
    def getPlugin(self, **qry_pars):
        """
        Browser Plugins

        ----------

        This report shows which browser plugins your visitors had enabled. This
        information might be important for choosing the right way to deliver
        your content.

        (dim: Plugin / cat: Visitors / subcat: Software)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_visits_percentage: % Visits

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=DevicePlugins.getPlugin&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=DevicePlugins.getPlugin&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=DevicePlugins.getPlugin&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=DevicePlugins.getPlugin&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModDevicesDetection:
    """
    The DevicesDetection API lets you access reports on your visitors devices,
    brands, models, Operating system, Browsers.
    """
    pass

    @method_decorator
    def getType(self, **qry_pars):
        """
        Device type

        ----------

        This report shows the types of devices your visitors were using. This
        report will always show all device types Matomo is able to detect, even
        if there were no visits with a specific type.

        (dim: Device type / cat: Visitors / subcat: Devices)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getType&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getType&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getType&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getType&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getBrand(self, **qry_pars):
        """
        Device brand

        ----------

        This report shows the brands / manufacturers of the devices your
        visitors were using. In most cases this information is only available
        for non-desktop devices.

        (dim: Device brand / cat: Visitors / subcat: Devices)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrand&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrand&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrand&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrand&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getModel(self, **qry_pars):
        """
        Device model

        ----------

        This report shows the devices your visitors are using. Each model is
        displayed combined with the device brand as some model names are used by
        multiple brands.

        (dim: Device model / cat: Visitors / subcat: Devices)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getModel&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getModel&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getModel&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getModel&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getOsFamilies(self, **qry_pars):
        """
        Operating System families

        ----------

        This report shows you the operating systems your visitors are using
        grouped by operating system family. An operating system family consists
        of different versions or distributions.

        (dim: Operating system family / cat: Visitors / subcat: Software)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getOsFamilies&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getOsFamilies&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getOsFamilies&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getOsFamilies&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getOsVersions(self, **qry_pars):
        """
        Operating System versions

        ----------

        This report shows you the operating systems your visitors are using.
        Each version and distribution is shown separately.

        (dim: Operating system version / cat: Visitors / subcat: Software)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getOsVersions&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getOsVersions&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getOsVersions&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getOsVersions&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getBrowsers(self, **qry_pars):
        """
        Browsers

        ----------

        This report contains information about what kind of browser your
        visitors were using.

        (dim: Browser / cat: Visitors / subcat: Software)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowsers&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowsers&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowsers&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowsers&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getBrowserVersions(self, **qry_pars):
        """
        Browser version

        ----------

        This report contains information about what kind of browser your
        visitors were using. Each browser version is listed separately.

        (dim: Browser version / cat: Visitors / subcat: Software)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowserVersions&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowserVersions&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowserVersions&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowserVersions&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getBrowserEngines(self, **qry_pars):
        """
        Browser engines

        ----------

        This report shows your visitors' browsers broken down into browser
        engines.

        The most important information for web developers is what kind of
        rendering engine their visitors are using. The labels contain the names
        of the engines followed by the most common browser using that engine in
        brackets.

        (dim: Browser engine / cat: Visitors / subcat: Software)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowserEngines&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowserEngines&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowserEngines&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=DevicesDetection.getBrowserEngines&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModEvents:
    """
    The Events API lets you request reports about your users' Custom Events.
    Events are tracked using the Javascript Tracker trackEvent() function, or
    using the [Tracking HTTP
    API](http://developer.matomo.org/api-reference/tracking-api).

    An event is defined by an event category (Videos, Music, Games...), an event
    action (Play, Pause, Duration, Add Playlist, Downloaded, Clicked...), and an
    optional event name (a movie name, a song title, etc.) and an optional
    numeric value.

    This API exposes the following Custom Events reports: getCategory lists the
    top Event Categories, getAction lists the top Event Actions, getName lists
    the top Event Names.

    These Events report define the following metrics: nb_uniq_visitors,
    nb_visits, nb_events. If you define values for your events, you can expect
    to see the following metrics: nb_events_with_value, sum_event_value,
    min_event_value, max_event_value, avg_event_value

    The Events.get* reports can be used with an optional &secondaryDimension
    parameter. Secondary dimension is the dimension used in the sub-table of the
    Event report you are requesting.

    Here are the possible values of secondaryDimension:

    - For Events.getCategory you can set secondaryDimension to eventAction or
      eventName.

    - For Events.getAction you can set secondaryDimension to eventName or
      eventCategory.

    - For Events.getName you can set secondaryDimension to eventAction or
      eventCategory.

    For example, to request all Custom Events Categories, and for each, the top
    Event actions, you would request:
    method=Events.getCategory&secondaryDimension=eventAction&flat=1. You may
    also omit &flat=1 in which case, to get top Event actions for one Event
    category, use method=Events.getActionFromCategoryId passing it the
    &idSubtable= of this Event category.
    """
    pass

    @method_decorator
    def getCategory(self, **qry_pars):
        """
        Event Categories

        ----------

        This report shows the categories of each tracked event and how many
        times they occurred. You can view the event actions and names that were
        tracked along with each event category in each row's subtable. You can
        change which is shown by changing the secondary dimension with the link
        at the bottom of the report.

        (dim: Event Category / cat: Actions / subcat: Events)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / secondaryDimension / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_events: Events

        Total number of events

        - sum_event_value: Event value

        The sum of event values

        - min_event_value: Minimum Event value

        The minimum value for this event

        - max_event_value: Maximum Event value

        The maximum value for this event

        - nb_events_with_value: Events with a value

        Number of events where an Event value was set

        - avg_event_value: The average of all values for this event

        The average of all values for this event

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Events.getCategory&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Events.getCategory&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Events.getCategory&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Events.getCategory&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAction(self, **qry_pars):
        """
        Event Actions

        ----------

        This report shows you the number of times each event action occurred.
        You can view the event categories and names that were tracked along with
        each event action in the row's subtable. You can change which is shown
        by changing the secondary dimension with the link at the bottom of the
        report.

        (dim: Event Action / cat: Actions / subcat: Events)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / secondaryDimension / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_events: Events

        Total number of events

        - sum_event_value: Event value

        The sum of event values

        - min_event_value: Minimum Event value

        The minimum value for this event

        - max_event_value: Maximum Event value

        The maximum value for this event

        - nb_events_with_value: Events with a value

        Number of events where an Event value was set

        - avg_event_value: The average of all values for this event

        The average of all values for this event

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Events.getAction&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Events.getAction&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Events.getAction&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Events.getAction&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getName(self, **qry_pars):
        """
        Event Names

        ----------

        This report shows you the names associated with each tracked event and
        how many times they occurred. You can view the event actions and
        categories that were tracked along with each event name in each row's
        subtable. You can change which is shown by changing the secondary
        dimension with the link at the bottom of the report.

        (dim: Event Name / cat: Actions / subcat: Events)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / secondaryDimension / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_events: Events

        Total number of events

        - sum_event_value: Event value

        The sum of event values

        - min_event_value: Minimum Event value

        The minimum value for this event

        - max_event_value: Maximum Event value

        The maximum value for this event

        - nb_events_with_value: Events with a value

        Number of events where an Event value was set

        - avg_event_value: The average of all values for this event

        The average of all values for this event

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Events.getName&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Events.getName&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Events.getName&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Events.getName&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getActionFromCategoryId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNameFromCategoryId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCategoryFromActionId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNameFromActionId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getActionFromNameId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCategoryFromNameId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModFeedback:
    """
    API for plugin Feedback
    """
    pass

    @method_decorator
    def sendFeedbackForFeature(self, **qry_pars):
        """
        Parameters:

        featureName / like / message

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModFormAnalytics:
    """
    The Form Analytics API lets you 1) manage forms within Matomo and 2) request
    all your form analytics reports and metrics.

    1) You can create, update, delete forms, as well as request any form and
    also archive them.

    2) Request all metrics and reports about how users interact with your forms:

    - Form usage by page URL to see whether the same form is used differently on
      different pages.

    - Entry fields to see where they start filling out your forms.

    - Drop off fields to see where your users leave your forms.

    - Field timings report to see where your users spent the most time.

    - Field size report to see how much text your users type.

    - Most corrected fields report to learn more about where users have problems
      filling out your form.

    - Unneeded fields report to see which fields are often left blank.

    - Several evolution reports of all metrics to see how your forms perform
      over time.

    And the following metrics:

    - How often was a form field interacted with (eg. focus or change).

    - Which fields did your visitors interact with first when they started
      filling out a form.

    - Which fields caused a visitor to stop filling out a form (drop offs).

    - How often your visitors changed a form field or made amendments.

    - How often a field was refocused or corrected (eg usage of backspace or
      delete key, cursor keys, …).

    - How much text they type into each of your text fields.

    - Which fields are unneeded and often left blank.

    - How long visitors hesitated (waited) before they started changing a field.

    - How much time your visitors spent on each field.
    """
    pass

    @method_decorator
    def addForm(self, **qry_pars):
        """
        Parameters:

        idSite / name / description / matchFormRules / matchPageRules /
        conversionRules

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateForm(self, **qry_pars):
        """
        Parameters:

        idSite / idForm / name / description / matchFormRules / matchPageRules /
        conversionRules

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getForm(self, **qry_pars):
        """
        Parameters:

        idSite / idForm

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getForms(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getForms&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getForms&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getForms&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getFormsByStatuses(self, **qry_pars):
        """
        Parameters:

        idSite / statuses

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteForm(self, **qry_pars):
        """
        Parameters:

        idSite / idForm

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def archiveForm(self, **qry_pars):
        """
        Parameters:

        idSite / idForm

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def get(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idForm / segment / columns

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.get&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.get&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.get&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.get&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getEntryFields(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idForm / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getDropOffFields(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idForm / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPageUrls(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idForm / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getFieldTimings(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idForm / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getFieldSize(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idForm / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUneededFields(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idForm / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getMostUsedFields(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idForm / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getFieldCorrections(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idForm / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateFormFieldDisplayName(self, **qry_pars):
        """
        Parameters:

        idSite / idForm / fields (cs-list)

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCounters(self, **qry_pars):
        """
        Parameters:

        idSite / lastMinutes / segment

        ----------

        Parameter examples:

        - idSite=1

        - lastMinutes=30

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getCounters&idSite=1&lastMinutes=30&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getCounters&idSite=1&lastMinutes=30&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getCounters&idSite=1&lastMinutes=30&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCurrentMostPopularForms(self, **qry_pars):
        """
        Parameters:

        idSite / lastMinutes / filter_limit / segment

        ----------

        Parameter examples:

        - idSite=1

        - lastMinutes=30

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        - filter_limit=5

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getCurrentMostPopularForms&idSite=1&lastMinutes=30&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getCurrentMostPopularForms&idSite=1&lastMinutes=30&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getCurrentMostPopularForms&idSite=1&lastMinutes=30&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAutoCreationSettings(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAutoCreationSettings&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAutoCreationSettings&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAutoCreationSettings&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableStatuses(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAvailableStatuses&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAvailableStatuses&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAvailableStatuses&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableFormRules(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAvailableFormRules&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAvailableFormRules&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAvailableFormRules&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailablePageRules(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAvailablePageRules&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAvailablePageRules&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=FormAnalytics.getAvailablePageRules&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModFunnels:
    """
    API for plugin Funnels
    """
    pass

    @method_decorator
    def getMetrics(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idFunnel / idGoal / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Funnels.getMetrics&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Funnels.getMetrics&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Funnels.getMetrics&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Funnels.getMetrics&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getFunnelFlow(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idFunnel / idGoal / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Funnels.getFunnelFlow&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Funnels.getFunnelFlow&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Funnels.getFunnelFlow&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Funnels.getFunnelFlow&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getFunnelEntries(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idFunnel / segment / step / expanded /
        idSubtable

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getFunnelExits(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idFunnel / segment / step

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getGoalFunnel(self, **qry_pars):
        """
        Parameters:

        idSite / idGoal

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAllActivatedFunnelsForSite(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Funnels.getAllActivatedFunnelsForSite&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Funnels.getAllActivatedFunnelsForSite&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Funnels.getAllActivatedFunnelsForSite&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def hasAnyActivatedFunnelForSite(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Funnels.hasAnyActivatedFunnelForSite&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Funnels.hasAnyActivatedFunnelForSite&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Funnels.hasAnyActivatedFunnelForSite&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteGoalFunnel(self, **qry_pars):
        """
        Parameters:

        idSite / idGoal

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setGoalFunnel(self, **qry_pars):
        """
        Parameters:

        idSite / idGoal / isActivated / steps

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailablePatternMatches(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Funnels.getAvailablePatternMatches&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Funnels.getAvailablePatternMatches&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Funnels.getAvailablePatternMatches&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def testUrlMatchesSteps(self, **qry_pars):
        """
        Parameters:

        url / steps

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModGoals:
    """
    Goals API lets you Manage existing goals, via "updateGoal" and "deleteGoal",
    create new Goals via "addGoal", or list existing Goals for one or several
    websites via "getGoals" If you are tracking Ecommerce orders and products on
    your site, the functions "getItemsSku", "getItemsName" and
    "getItemsCategory" will return the list of products purchased on your site,
    either grouped by Product SKU, Product Name or Product Category. For each
    name, SKU or category, the following metrics are returned: Total revenue,
    Total quantity, average price, average quantity, number of orders (or
    abandoned carts) containing this product, number of visits on the Product
    page, Conversion rate. By default, these functions return the 'Products
    purchased'. These functions also accept an optional parameter
    &abandonedCarts=1. If the parameter is set, it will instead return the
    metrics for products that were left in an abandoned cart therefore not
    purchased. The API also lets you request overall Goal metrics via the method
    "get": Conversions, Visits with at least one conversion, Conversion rate and
    Revenue. If you wish to request specific metrics about Ecommerce goals, you
    can set the parameter &idGoal=ecommerceAbandonedCart to get metrics about
    abandoned carts (including Lost revenue, and number of items left in the
    cart) or &idGoal=ecommerceOrder to get metrics about Ecommerce orders
    (number of orders, visits with an order, subtotal, tax, shipping, discount,
    revenue, items ordered) See also the documentation about Tracking Goals in
    Matomo.
    """
    pass

    @method_decorator
    def getGoal(self, **qry_pars):
        """
        Parameters:

        idSite / idGoal

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getGoals(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Goals.getGoals&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Goals.getGoals&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Goals.getGoals&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addGoal(self, **qry_pars):
        """
        Parameters:

        idSite / name / matchAttribute / pattern / patternType / caseSensitive /
        revenue / allowMultipleConversionsPerVisit / description /
        useEventValueAsRevenue

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateGoal(self, **qry_pars):
        """
        Parameters:

        idSite / idGoal / name / matchAttribute / pattern / patternType /
        caseSensitive / revenue / allowMultipleConversionsPerVisit / description
        / useEventValueAsRevenue

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteGoal(self, **qry_pars):
        """
        Parameters:

        idSite / idGoal

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getItemsSku(self, **qry_pars):
        """
        Product SKU

        ----------

        (dim: Product SKU / cat: Ecommerce / subcat: Products)

        ----------

        Parameters:

        idSite / period / date / abandonedCarts / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - abandonedCarts=0

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - revenue: Product Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - quantity: Quantity

        Quantity is the total number of products sold for each Product
        SKU/Name/Category.

        - orders: Unique Purchases

        It is the total number of Ecommerce orders which contained this Product
        SKU/Name/Category at least once.

        - nb_visits: Visits

        This value appears only if you have set up 'Ecommerce Product/Category
        page tracking'. The number of visits on the Product/Category page.

        - avg_price: Average Price

        The average revenue for this Product/Category.

        - avg_quantity: Average Quantity

        The average quantity for this Product/Category.

        - conversion_rate: Product Conversion Rate

        This value appears only if you have set up 'Ecommerce Product/Category
        page tracking'. The conversion rate is the number of orders (or
        abandoned_carts if the request contains '&abandonedCarts=1') containing
        this product/category divided by number of visits on the
        product/category page.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsSku&idSite=1&period=day&date=yesterday&abandonedCarts=0&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsSku&idSite=1&period=day&date=yesterday&abandonedCarts=0&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsSku&idSite=1&period=day&date=yesterday&abandonedCarts=0&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsSku&idSite=1&period=day&date=last10&abandonedCarts=0&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getItemsName(self, **qry_pars):
        """
        Product Name

        ----------

        (dim: Product Name / cat: Ecommerce / subcat: Products)

        ----------

        Parameters:

        idSite / period / date / abandonedCarts / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - abandonedCarts=0

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - revenue: Product Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - quantity: Quantity

        Quantity is the total number of products sold for each Product
        SKU/Name/Category.

        - orders: Unique Purchases

        It is the total number of Ecommerce orders which contained this Product
        SKU/Name/Category at least once.

        - nb_visits: Visits

        This value appears only if you have set up 'Ecommerce Product/Category
        page tracking'. The number of visits on the Product/Category page.

        - avg_price: Average Price

        The average revenue for this Product/Category.

        - avg_quantity: Average Quantity

        The average quantity for this Product/Category.

        - conversion_rate: Product Conversion Rate

        This value appears only if you have set up 'Ecommerce Product/Category
        page tracking'. The conversion rate is the number of orders (or
        abandoned_carts if the request contains '&abandonedCarts=1') containing
        this product/category divided by number of visits on the
        product/category page.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsName&idSite=1&period=day&date=yesterday&abandonedCarts=0&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsName&idSite=1&period=day&date=yesterday&abandonedCarts=0&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsName&idSite=1&period=day&date=yesterday&abandonedCarts=0&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsName&idSite=1&period=day&date=last10&abandonedCarts=0&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getItemsCategory(self, **qry_pars):
        """
        Product Category

        ----------

        (dim: Product Category / cat: Ecommerce / subcat: Products)

        ----------

        Parameters:

        idSite / period / date / abandonedCarts / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - abandonedCarts=0

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - revenue: Product Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - quantity: Quantity

        Quantity is the total number of products sold for each Product
        SKU/Name/Category.

        - orders: Unique Purchases

        It is the total number of Ecommerce orders which contained this Product
        SKU/Name/Category at least once.

        - nb_visits: Visits

        This value appears only if you have set up 'Ecommerce Product/Category
        page tracking'. The number of visits on the Product/Category page.

        - avg_price: Average Price

        The average revenue for this Product/Category.

        - avg_quantity: Average Quantity

        The average quantity for this Product/Category.

        - conversion_rate: Product Conversion Rate

        This value appears only if you have set up 'Ecommerce Product/Category
        page tracking'. The conversion rate is the number of orders (or
        abandoned_carts if the request contains '&abandonedCarts=1') containing
        this product/category divided by number of visits on the
        product/category page.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsCategory&idSite=1&period=day&date=yesterday&abandonedCarts=0&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsCategory&idSite=1&period=day&date=yesterday&abandonedCarts=0&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsCategory&idSite=1&period=day&date=yesterday&abandonedCarts=0&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Goals.getItemsCategory&idSite=1&period=day&date=last10&abandonedCarts=0&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def get(self, **qry_pars):
        """
        Goal View Submit Job

        ----------

        This report gives an overview of how well your visitors convert a
        specific goal.

        (cat: Goals)

        ----------

        Parameters:

        idSite / period / date / segment / idGoal / columns (cs-list) /
        showAllGoalSpecificMetrics / compare

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_conversions: Conversions

        Number of goal conversions.

        - nb_visits_converted: Visits with Conversions

        Number of visits that converted a goal.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Goals.get&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Goals.get&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Goals.get&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Goals.get&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getDaysToConversion(self, **qry_pars):
        """
        View Submit Job - Days to Conversion

        ----------

        This report shows how many days pass before your visitors convert a
        goal.

        (dim: Days to Conversion / cat: Goals)

        ----------

        Parameters:

        idSite / period / date / segment / idGoal

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_conversions: Conversions

        Number of goal conversions.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Goals.getDaysToConversion&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Goals.getDaysToConversion&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Goals.getDaysToConversion&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Goals.getDaysToConversion&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getVisitsUntilConversion(self, **qry_pars):
        """
        View Submit Job - Visits to Conversion

        ----------

        This report shows the number of visits made before a visitor converts a
        goal.

        (dim: Visits to Conversion / cat: Goals)

        ----------

        Parameters:

        idSite / period / date / segment / idGoal

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_conversions: Conversions

        Number of goal conversions.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Goals.getVisitsUntilConversion&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Goals.getVisitsUntilConversion&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Goals.getVisitsUntilConversion&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Goals.getVisitsUntilConversion&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModHeatmapSessionRecording:
    """
    API for plugin Heatmap & Session Recording. When you request activity data
    for a heatmap or a recorded session, please note that any X or Y coordinate,
    scroll reach position, and above the fold is relative and not absolute. X
    and Y coordinate are between 0 and 2000 and are relative to the selector
    where 2000 means the position is at 100% of the element, 1000 means the
    position is at 50% and 0 means the position is actually 0 pixel from the
    element. Scroll and above the fold positions are between 0 and 1000. If for
    example a web page is 3000 pixel high, and scroll reach is 100, it means the
    user has seen the content up to 300 pixels (10%, or 100 of 1000). We
    differentiate between two different IDs here: idSiteHsr represents the ID of
    a heatmap or session recording configuration idLogHsr represents the ID of
    an actually recorded / tracked session or heatmap activity
    """
    pass

    @method_decorator
    def addHeatmap(self, **qry_pars):
        """
        Parameters:

        idSite / name / matchPageRules / sampleLimit / sampleRate /
        excludedElements / screenshotUrl / breakpointMobile / breakpointTablet

        ----------

        Parameter examples:

        - sampleLimit=1000

        - sampleRate=5

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateHeatmap(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr / name / matchPageRules / sampleLimit / sampleRate /
        excludedElements / screenshotUrl / breakpointMobile / breakpointTablet

        ----------

        Parameter examples:

        - sampleLimit=1000

        - sampleRate=5

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteHeatmapScreenshot(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addSessionRecording(self, **qry_pars):
        """
        Parameters:

        idSite / name / matchPageRules (cs-list) / sampleLimit / sampleRate /
        minSessionTime / requiresActivity / captureKeystrokes

        ----------

        Parameter examples:

        - sampleLimit=1000

        - sampleRate=10

        - minSessionTime=0

        - requiresActivity=1

        - captureKeystrokes=1

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateSessionRecording(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr / name / matchPageRules (cs-list) / sampleLimit /
        sampleRate / minSessionTime / requiresActivity / captureKeystrokes

        ----------

        Parameter examples:

        - sampleLimit=1000

        - sampleRate=10

        - minSessionTime=0

        - requiresActivity=1

        - captureKeystrokes=1

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getHeatmap(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSessionRecording(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteHeatmap(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def endHeatmap(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteSessionRecording(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def endSessionRecording(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getHeatmaps(self, **qry_pars):
        """
        Parameters:

        idSite / includePageTreeMirror

        ----------

        Parameter examples:

        - idSite=1

        - includePageTreeMirror=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getHeatmaps&idSite=1&includePageTreeMirror=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getHeatmaps&idSite=1&includePageTreeMirror=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getHeatmaps&idSite=1&includePageTreeMirror=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSessionRecordings(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getSessionRecordings&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getSessionRecordings&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getSessionRecordings&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getRecordedSessions(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSiteHsr / segment / idSubtable

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getRecordedSession(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr / idLogHsr

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteRecordedSession(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr / idVisit

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteRecordedPageview(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr / idLogHsr

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getRecordedHeatmapMetadata(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSiteHsr / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getRecordedHeatmap(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSiteHsr / heatmapType / deviceType / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getEmbedSessionInfo(self, **qry_pars):
        """
        Parameters:

        idSite / idSiteHsr / idLogHsr

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def testUrlMatchPages(self, **qry_pars):
        """
        Parameters:

        url / matchPageRules (cs-list)

        ----------

        Parameter examples:

        - url=https://divezone.net/

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.testUrlMatchPages&url=https://divezone.net/&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.testUrlMatchPages&url=https://divezone.net/&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.testUrlMatchPages&url=https://divezone.net/&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableStatuses(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableStatuses&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableStatuses&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableStatuses&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableTargetPageRules(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableTargetPageRules&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableTargetPageRules&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableTargetPageRules&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableDeviceTypes(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableDeviceTypes&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableDeviceTypes&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableDeviceTypes&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableHeatmapTypes(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableHeatmapTypes&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableHeatmapTypes&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableHeatmapTypes&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableSessionRecordingSampleLimits(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableSessionRecordingSampleLimits&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableSessionRecordingSampleLimits&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getAvailableSessionRecordingSampleLimits&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getEventTypes(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getEventTypes&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getEventTypes&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=HeatmapSessionRecording.getEventTypes&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModImageGraph:
    """
    The ImageGraph.get API call lets you generate beautiful static PNG Graphs
    for any existing Matomo report. Supported graph types are: line plot, 2D/3D
    pie chart and vertical bar chart. A few notes about some of the parameters
    available:

    - $graphType defines the type of graph plotted, accepted values are:
      'evolution', 'verticalBar', 'pie' and '3dPie'

    - $colors accepts a comma delimited list of colors that will overwrite the
      default Matomo colors

    - you can also customize the width, height, font size, metric being plotted
      (in case the data contains multiple columns/metrics). See also How to
      embed static Image Graphs? for more information.
    """
    pass

    @method_decorator
    def get(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / apiModule / apiAction / graphType / outputType
        / columns / labels / showLegend / width / height / fontSize /
        legendFontSize / aliasedGraph / idGoal / colors / textColor /
        backgroundColor / gridColor / idSubtable / legendAppendMetric / segment
        / idDimension

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - apiModule=UserCountry

        - apiAction=getCountry

        - outputType=0

        - showLegend=1

        - fontSize=9

        - aliasedGraph=1

        - textColor=222222

        - backgroundColor=FFFFFF

        - gridColor=CCCCCC

        - legendAppendMetric=1

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=ImageGraph.get&idSite=1&period=day&date=yesterday&apiModule=UserCountry&apiAction=getCountry&outputType=0&showLegend=1&fontSize=9&aliasedGraph=1&textColor=222222&backgroundColor=FFFFFF&gridColor=CCCCCC&legendAppendMetric=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=ImageGraph.get&idSite=1&period=day&date=yesterday&apiModule=UserCountry&apiAction=getCountry&outputType=0&showLegend=1&fontSize=9&aliasedGraph=1&textColor=222222&backgroundColor=FFFFFF&gridColor=CCCCCC&legendAppendMetric=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=ImageGraph.get&idSite=1&period=day&date=yesterday&apiModule=UserCountry&apiAction=getCountry&outputType=0&showLegend=1&fontSize=9&aliasedGraph=1&textColor=222222&backgroundColor=FFFFFF&gridColor=CCCCCC&legendAppendMetric=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=ImageGraph.get&idSite=1&period=day&date=last10&apiModule=UserCountry&apiAction=getCountry&outputType=0&showLegend=1&fontSize=9&aliasedGraph=1&textColor=222222&backgroundColor=FFFFFF&gridColor=CCCCCC&legendAppendMetric=1&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModInsights:
    """
    API for plugin Insights
    """
    pass

    @method_decorator
    def canGenerateInsights(self, **qry_pars):
        """
        Parameters:

        date / period

        ----------

        Parameter examples:

        - date=yesterday / date=last10

        - period=day

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Insights.canGenerateInsights&date=yesterday&period=day&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Insights.canGenerateInsights&date=yesterday&period=day&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Insights.canGenerateInsights&date=yesterday&period=day&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Insights.canGenerateInsights&date=last10&period=day&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getInsightsOverview(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Insights.getInsightsOverview&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Insights.getInsightsOverview&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Insights.getInsightsOverview&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Insights.getInsightsOverview&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getMoversAndShakersOverview(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Insights.getMoversAndShakersOverview&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Insights.getMoversAndShakersOverview&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Insights.getMoversAndShakersOverview&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Insights.getMoversAndShakersOverview&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getMoversAndShakers(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / reportUniqueId / segment / comparedToXPeriods /
        limitIncreaser / limitDecreaser

        ----------

        Parameter examples:

        - comparedToXPeriods=1

        - limitIncreaser=4

        - limitDecreaser=4

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getInsights(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / reportUniqueId / segment / limitIncreaser /
        limitDecreaser / filterBy / minImpactPercent / minGrowthPercent /
        comparedToXPeriods / orderBy

        ----------

        Parameter examples:

        - limitIncreaser=5

        - limitDecreaser=5

        - minImpactPercent=2

        - minGrowthPercent=20

        - comparedToXPeriods=1

        - orderBy=absolute

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModLanguagesManager:
    """
    The LanguagesManager API lets you access existing Matomo translations, and
    change Users languages preferences. "getTranslationsForLanguage" will return
    all translation strings for a given language, so you can leverage Matomo
    translations in your application (and automatically benefit from the 40+
    translations!). This is mostly useful to developers who integrate Matomo API
    results in their own application. You can also request the default language
    to load for a user via "getLanguageForUser", or update it via
    "setLanguageForUser".
    """
    pass

    @method_decorator
    def isLanguageAvailable(self, **qry_pars):
        """
        Parameters:

        languageCode

        ----------

        Parameter examples:

        - languageCode=fr

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.isLanguageAvailable&languageCode=fr&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.isLanguageAvailable&languageCode=fr&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.isLanguageAvailable&languageCode=fr&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableLanguages(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getAvailableLanguages&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getAvailableLanguages&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getAvailableLanguages&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableLanguagesInfo(self, **qry_pars):
        """
        Parameters:

        excludeNonCorePlugins

        ----------

        Parameter examples:

        - excludeNonCorePlugins=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getAvailableLanguagesInfo&excludeNonCorePlugins=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getAvailableLanguagesInfo&excludeNonCorePlugins=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getAvailableLanguagesInfo&excludeNonCorePlugins=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableLanguageNames(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getAvailableLanguageNames&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getAvailableLanguageNames&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getAvailableLanguageNames&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getTranslationsForLanguage(self, **qry_pars):
        """
        Parameters:

        languageCode

        ----------

        Parameter examples:

        - languageCode=fr

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getTranslationsForLanguage&languageCode=fr&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getTranslationsForLanguage&languageCode=fr&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=LanguagesManager.getTranslationsForLanguage&languageCode=fr&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getLanguageForUser(self, **qry_pars):
        """
        Parameters:

        login

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setLanguageForUser(self, **qry_pars):
        """
        Parameters:

        login / languageCode

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def uses12HourClockForUser(self, **qry_pars):
        """
        Parameters:

        login

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def set12HourClockForUser(self, **qry_pars):
        """
        Parameters:

        login / use12HourClock

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModLive:
    """
    The Live! API lets you access complete visit level information about your
    visitors. Combined with the power of Segmentation, you will be able to
    request visits filtered by any criteria. The method "getLastVisitsDetails"
    will return extensive data for each visit, which includes: server time,
    visitId, visitorId, visitorType (new or returning), number of pages, list of
    all pages (and events, file downloaded and outlinks clicked), custom
    variables names and values set to this visit, number of goal conversions
    (and list of all Goal conversions for this visit, with time of conversion,
    revenue, URL, etc.), but also other attributes such as: days since last
    visit, days since first visit, country, continent, visitor IP, provider,
    referrer used (referrer name, keyword if it was a search engine, full URL),
    campaign name and keyword, operating system, browser, type of screen,
    resolution, supported browser plugins (flash, java, silverlight, pdf, etc.),
    various dates & times format to make it easier for API users... and more!
    With the parameter '&segment=' you can filter the returned visits by any
    criteria (visitor IP, visitor ID, country, keyword used, time of day, etc.).
    The method "getCounters" is used to return a simple counter: visits, number
    of actions, number of converted visits, in the last N minutes. See also the
    documentation about Real time widget and visitor level reports in Matomo.
    """
    pass

    @method_decorator
    def getCounters(self, **qry_pars):
        """
        Parameters:

        idSite / lastMinutes / segment / showColumns (cs-list) / hideColumns
        (cs-list)

        ----------

        Parameter examples:

        - idSite=1

        - lastMinutes=30

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Live.getCounters&idSite=1&lastMinutes=30&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Live.getCounters&idSite=1&lastMinutes=30&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Live.getCounters&idSite=1&lastMinutes=30&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getLastVisitsDetails(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment / countVisitorsToFetch / minTimestamp /
        flat / doNotFetchActions / enhanced

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Live.getLastVisitsDetails&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Live.getLastVisitsDetails&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Live.getLastVisitsDetails&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Live.getLastVisitsDetails&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getVisitorProfile(self, **qry_pars):
        """
        Parameters:

        idSite / visitorId / segment / limitVisits

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Live.getVisitorProfile&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Live.getVisitorProfile&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Live.getVisitorProfile&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getMostRecentVisitorId(self, **qry_pars):
        """
        Parameters:

        idSite / segment

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Live.getMostRecentVisitorId&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Live.getMostRecentVisitorId&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Live.getMostRecentVisitorId&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModLogin:
    """
    API for plugin Login
    """
    pass

    @method_decorator
    def unblockBruteForceIPs(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Login.unblockBruteForceIPs&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Login.unblockBruteForceIPs&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Login.unblockBruteForceIPs&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModMarketingCampaignsReporting:
    """
    API for plugin MarketingCampaignsReporting
    """
    pass

    @method_decorator
    def getId(self, **qry_pars):
        """
        Campaign Ids

        ----------

        (dim: Campaign Id / cat: Referrers / subcat: Campaigns)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getId&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getId&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getId&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getId&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getName(self, **qry_pars):
        """
        Campaign Names

        ----------

        (dim: Campaign Name / cat: Referrers / subcat: Campaigns)

        ----------

        Parameters:

        idSite / period / date / segment / expanded

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getName&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getName&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getName&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getName&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywordContentFromNameId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeyword(self, **qry_pars):
        """
        Campaign Keywords

        ----------

        (dim: Campaign Keyword / cat: Referrers / subcat: Campaigns)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getKeyword&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getKeyword&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getKeyword&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getKeyword&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSource(self, **qry_pars):
        """
        Campaign Sources

        ----------

        (dim: Campaign Source / cat: Referrers / subcat: Campaigns)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getSource&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getSource&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getSource&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getSource&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getMedium(self, **qry_pars):
        """
        Campaign Mediums

        ----------

        (dim: Campaign Medium / cat: Referrers / subcat: Campaigns)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getMedium&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getMedium&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getMedium&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getMedium&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContent(self, **qry_pars):
        """
        Campaign Contents

        ----------

        (dim: Campaign Content / cat: Referrers / subcat: Campaigns)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getContent&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getContent&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getContent&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getContent&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getGroup(self, **qry_pars):
        """
        Campaign Groups

        ----------

        (dim: Campaign Group / cat: Referrers / subcat: Campaigns)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getGroup&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getGroup&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getGroup&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getGroup&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPlacement(self, **qry_pars):
        """
        Campaign Placements

        ----------

        (dim: Campaign Placement / cat: Referrers / subcat: Campaigns)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getPlacement&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getPlacement&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getPlacement&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getPlacement&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSourceMedium(self, **qry_pars):
        """
        Campaign Source - Medium

        ----------

        (dim: Source - Medium / cat: Referrers / subcat: Campaigns)

        ----------

        Parameters:

        idSite / period / date / segment / expanded

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getSourceMedium&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getSourceMedium&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getSourceMedium&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MarketingCampaignsReporting.getSourceMedium&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNameFromSourceMediumId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModMediaAnalytics:
    """
    The MediaAnalytics API lets you request your reports about how your Video
    and Audio are accessed and viewed on your websites and apps. Some of the
    methods return Real Time information (similarly to the Live! API), while
    others return all your videos and audios and their key metrics.

    The real time methods can return information about the last N minutes (or
    last N hours). They include the following:

    - the method getCurrentNumPlays returns the number of video plays (and audio
      plays) in the last N minutes

    - the method getCurrentSumTimeSpent returns the the total time users spent
      playing your media in the last N minutes

    - the method getCurrentMostPlays returns the most popular videos in the last
      N minutes.

    The other methods return the aggregated analytics reports for Video and
    Audio:

    - MediaAnalytics.get returns the overall metrics for your videos and audios:
      nb_plays, nb_unique_visitors_plays, nb_impressions,
      nb_unique_visitors_impressions, nb_finishes, sum_total_time_watched,
      sum_total_audio_plays, sum_total_audio_impressions, sum_total_video_plays,
      sum_total_video_impressions, play_rate, finish_rate, impression_rate.

    - getVideoTitles and getAudioTitles return the list of videos / audio by
      video title and audio title.

    - getGroupedVideoResources and getGroupedAudioResources return the list of
      watched videos / audio grouped by resource URL. The "grouped media
      resource" report displays a flat report which includes both the domain and
      the path to the media resource, whereas the regular "media resource"
      report displays a hierarchical view of your media resources by domain.

    - getVideoHours and getAudioHours return the list of videos / audio by by
      hour (to see how your media is consumed at a different time of the day).

    - getVideoTitles and getAudioTitles return the list of videos / audio by
      video title and audio title.

    - getVideoResolutions return the list of videos by player resolution (see
      how your videos are consumed when the video resolution varies).

    - getPlayers return the watched media by media player.
    """
    pass

    @method_decorator
    def hasRecords(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.hasRecords&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.hasRecords&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.hasRecords&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def get(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment / columns

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.get&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.get&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.get&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.get&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCurrentNumPlays(self, **qry_pars):
        """
        Parameters:

        idSite / lastMinutes / segment

        ----------

        Parameter examples:

        - idSite=1

        - lastMinutes=30

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getCurrentNumPlays&idSite=1&lastMinutes=30&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getCurrentNumPlays&idSite=1&lastMinutes=30&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getCurrentNumPlays&idSite=1&lastMinutes=30&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCurrentSumTimeSpent(self, **qry_pars):
        """
        Parameters:

        idSite / lastMinutes / segment

        ----------

        Parameter examples:

        - idSite=1

        - lastMinutes=30

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getCurrentSumTimeSpent&idSite=1&lastMinutes=30&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getCurrentSumTimeSpent&idSite=1&lastMinutes=30&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getCurrentSumTimeSpent&idSite=1&lastMinutes=30&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCurrentMostPlays(self, **qry_pars):
        """
        Parameters:

        idSite / lastMinutes / filter_limit / segment

        ----------

        Parameter examples:

        - idSite=1

        - lastMinutes=30

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        - filter_limit=5

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getCurrentMostPlays&idSite=1&lastMinutes=30&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getCurrentMostPlays&idSite=1&lastMinutes=30&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getCurrentMostPlays&idSite=1&lastMinutes=30&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getVideoResources(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment / idSubtable / secondaryDimension /
        expanded

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoResources&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoResources&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoResources&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoResources&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAudioResources(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment / idSubtable / secondaryDimension /
        expanded

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioResources&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioResources&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioResources&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioResources&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getVideoTitles(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment / idSubtable / secondaryDimension

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoTitles&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoTitles&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoTitles&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoTitles&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAudioTitles(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment / idSubtable / secondaryDimension

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioTitles&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioTitles&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioTitles&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioTitles&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getGroupedVideoResources(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment / idSubtable / secondaryDimension

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getGroupedVideoResources&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getGroupedVideoResources&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getGroupedVideoResources&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getGroupedVideoResources&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getGroupedAudioResources(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment / idSubtable / secondaryDimension

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getGroupedAudioResources&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getGroupedAudioResources&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getGroupedAudioResources&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getGroupedAudioResources&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getVideoHours(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoHours&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoHours&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoHours&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoHours&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAudioHours(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioHours&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioHours&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioHours&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getAudioHours&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getVideoResolutions(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoResolutions&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoResolutions&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoResolutions&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getVideoResolutions&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPlayers(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getPlayers&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getPlayers&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getPlayers&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MediaAnalytics.getPlayers&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModMobileMessaging:
    """
    The MobileMessaging API lets you manage and access all the MobileMessaging
    plugin features including : - manage SMS API credential - activate phone
    numbers - check remaining credits - send SMS
    """
    pass

    @method_decorator
    def areSMSAPICredentialProvided(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.areSMSAPICredentialProvided&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.areSMSAPICredentialProvided&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.areSMSAPICredentialProvided&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSMSProvider(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.getSMSProvider&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.getSMSProvider&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.getSMSProvider&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setSMSAPICredential(self, **qry_pars):
        """
        Parameters:

        provider / credentials (cs-list)

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addPhoneNumber(self, **qry_pars):
        """
        Parameters:

        phoneNumber

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCreditLeft(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.getCreditLeft&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.getCreditLeft&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.getCreditLeft&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def removePhoneNumber(self, **qry_pars):
        """
        Parameters:

        phoneNumber

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def validatePhoneNumber(self, **qry_pars):
        """
        Parameters:

        phoneNumber / verificationCode

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteSMSAPICredential(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.deleteSMSAPICredential&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.deleteSMSAPICredential&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.deleteSMSAPICredential&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setDelegatedManagement(self, **qry_pars):
        """
        Parameters:

        delegatedManagement

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getDelegatedManagement(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.getDelegatedManagement&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.getDelegatedManagement&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MobileMessaging.getDelegatedManagement&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModMultiChannelConversionAttribution:
    """
    Multi Channel Conversion Attribution API
    """
    pass

    @method_decorator
    def setGoalAttribution(self, **qry_pars):
        """
        Parameters:

        idSite / idGoal / isEnabled

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getGoalAttribution(self, **qry_pars):
        """
        Parameters:

        idSite / idGoal

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getChannelAttribution(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idGoal / numDaysPriorToConversion / segment /
        expanded / flat / idSubtable

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableNumDaysPriorConversion(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MultiChannelConversionAttribution.getAvailableNumDaysPriorConversion&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MultiChannelConversionAttribution.getAvailableNumDaysPriorConversion&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MultiChannelConversionAttribution.getAvailableNumDaysPriorConversion&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSiteAttributionGoals(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MultiChannelConversionAttribution.getSiteAttributionGoals&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MultiChannelConversionAttribution.getSiteAttributionGoals&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MultiChannelConversionAttribution.getSiteAttributionGoals&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModMultiSites:
    """
    The MultiSites API lets you request the key metrics (visits, page views,
    revenue) for all Websites in Matomo.
    """
    pass

    @method_decorator
    def getAll(self, **qry_pars):
        """
        All Websites dashboard

        ----------

        This report gives you an informational overview for each of your
        websites, containing the most general metrics about your visitors.

        (dim: Website / cat: All Websites)

        ----------

        Parameters:

        period / date / segment / enhanced / pattern / showColumns (cs-list)

        ----------

        Parameter examples:

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_pageviews: Pageviews

        The number of times this page was visited.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - nb_conversions: Conversions

        Number of goal conversions.

        - orders: Ecommerce Orders

        It is the total number of Ecommerce orders which contained this Product
        SKU/Name/Category at least once.

        - ecommerce_revenue: Product Revenue

        

        - visits_evolution: Visits Evolution

        

        - actions_evolution: Actions Evolution

        

        - pageviews_evolution: Pageviews Evolution

        

        - revenue_evolution: Revenue Evolution

        

        - nb_conversions_evolution: Conversions Evolution

        

        - orders_evolution: Ecommerce Orders Evolution

        

        - ecommerce_revenue_evolution: Product Revenue Evolution

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MultiSites.getAll&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MultiSites.getAll&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MultiSites.getAll&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MultiSites.getAll&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getOne(self, **qry_pars):
        """
        Single Website dashboard

        ----------

        This report gives you an informational overview for a specific website,
        containing the most general metrics about your visitors.

        (dim: Website / cat: All Websites)

        ----------

        Parameters:

        idSite / period / date / segment / enhanced

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_pageviews: Pageviews

        The number of times this page was visited.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - nb_conversions: Conversions

        Number of goal conversions.

        - orders: Ecommerce Orders

        It is the total number of Ecommerce orders which contained this Product
        SKU/Name/Category at least once.

        - ecommerce_revenue: Product Revenue

        

        - visits_evolution: Visits Evolution

        

        - actions_evolution: Actions Evolution

        

        - pageviews_evolution: Pageviews Evolution

        

        - revenue_evolution: Revenue Evolution

        

        - nb_conversions_evolution: Conversions Evolution

        

        - orders_evolution: Ecommerce Orders Evolution

        

        - ecommerce_revenue_evolution: Product Revenue Evolution

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=MultiSites.getOne&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=MultiSites.getOne&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=MultiSites.getOne&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=MultiSites.getOne&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModOverlay:
    """
    Class API
    """
    pass

    @method_decorator
    def getTranslations(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Overlay.getTranslations&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Overlay.getTranslations&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Overlay.getTranslations&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getExcludedQueryParameters(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Overlay.getExcludedQueryParameters&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Overlay.getExcludedQueryParameters&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Overlay.getExcludedQueryParameters&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getFollowingPages(self, **qry_pars):
        """
        Parameters:

        url / idSite / period / date / segment

        ----------

        Parameter examples:

        - url=https://divezone.net/

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Overlay.getFollowingPages&url=https://divezone.net/&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Overlay.getFollowingPages&url=https://divezone.net/&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Overlay.getFollowingPages&url=https://divezone.net/&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Overlay.getFollowingPages&url=https://divezone.net/&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModPagePerformance:
    """
    This API module is not documented.
    """
    pass

    @method_decorator
    def get(self, **qry_pars):
        """
        Performance overview

        ----------

        This report provides an overview of how fast your webpages become
        visible to your visitors. This includes both how long it takes for
        browsers to download your webpages and how long it takes for browsers to
        display them.

        (cat: Actions / subcat: Performance)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - avg_time_network: Avg. network time

        Average time (in seconds) it takes to connect to the server. This
        includes the time needed to lookup DNS and establish a TCP connection.
        This value might be 0 after the first request to a domain as the browser
        might cache the connection.

        - avg_time_server: Avg. server time

        Average time (in seconds) it takes the server to generate the page. This
        is the time between the server receiving the request and starting to
        serve the response.

        - avg_time_transfer: Avg. transfer time

        Average time (in seconds) it takes the browser to download the response
        from the server. This is the time from receiving the first byte till the
        response is complete.

        - avg_time_dom_processing: Avg. DOM processing time

        Average time (in seconds) the browser spends loading the webpage after
        the response was fully received and before the user can start
        interacting with it.

        - avg_time_dom_completion: Avg. DOM completion time

        Average time (in seconds) it takes for the browser to load media and
        execute any Javascript code listening for the DOMContentLoaded event
        after the webpage was loaded and the user can already interact with it.

        - avg_time_on_load: Avg. on load time

        Average time (in seconds) it takes the browser to execute Javascript
        code waiting for the window.load event. This event is triggered once the
        DOM has completely rendered.

        - avg_page_load_time: Avg. page load time

        Average time (in seconds) it takes from requesting a page until the page
        is fully rendered within the browser

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=PagePerformance.get&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=PagePerformance.get&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=PagePerformance.get&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=PagePerformance.get&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModPrivacyManager:
    """
    API for plugin PrivacyManage
    """
    pass

    @method_decorator
    def deleteDataSubjects(self, **qry_pars):
        """
        Parameters:

        visits

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def exportDataSubjects(self, **qry_pars):
        """
        Parameters:

        visits

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def findDataSubjects(self, **qry_pars):
        """
        Parameters:

        idSite / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def anonymizeSomeRawData(self, **qry_pars):
        """
        Parameters:

        idSites / date / anonymizeIp / anonymizeLocation / anonymizeUserId /
        unsetVisitColumns (cs-list) / unsetLinkVisitActionColumns (cs-list)

        ----------

        Parameter examples:

        - idSites=1,2

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=PrivacyManager.anonymizeSomeRawData&idSites=1,2&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=PrivacyManager.anonymizeSomeRawData&idSites=1,2&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=PrivacyManager.anonymizeSomeRawData&idSites=1,2&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=PrivacyManager.anonymizeSomeRawData&idSites=1,2&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableVisitColumnsToAnonymize(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=PrivacyManager.getAvailableVisitColumnsToAnonymize&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=PrivacyManager.getAvailableVisitColumnsToAnonymize&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=PrivacyManager.getAvailableVisitColumnsToAnonymize&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableLinkVisitActionColumnsToAnonymize(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=PrivacyManager.getAvailableLinkVisitActionColumnsToAnonymize&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=PrivacyManager.getAvailableLinkVisitActionColumnsToAnonymize&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=PrivacyManager.getAvailableLinkVisitActionColumnsToAnonymize&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModReferrers:
    """
    The Referrers API lets you access reports about Websites, Search engines,
    Keywords, Campaigns used to access your website. For example, "getKeywords"
    returns all search engine keywords (with general analytics metrics for each
    keyword), "getWebsites" returns referrer websites (along with the full
    Referrer URL if the parameter &expanded=1 is set). "getReferrerType" returns
    the Referrer overview report. "getCampaigns" returns the list of all
    campaigns (and all campaign keywords if the parameter &expanded=1 is set).
    """
    pass

    @method_decorator
    def get(self, **qry_pars):
        """
        Referrers Overview

        ----------

        This report shows what acquisition channels your visitors used to get to
        your website, and the number of visits each channel type is responsible
        for.

        (cat: Referrers)

        ----------

        Parameters:

        idSite / period / date / segment / columns

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - Referrers_visitorsFromSearchEngines: Visitors from Search Engines

        

        - Referrers_visitorsFromSearchEngines_percent: Percent of Visitors from
          Search Engines

        

        - Referrers_visitorsFromSocialNetworks: Visitors from Social Networks

        

        - Referrers_visitorsFromSocialNetworks_percent: Percent of Visitors from
          Social Networks

        

        - Referrers_visitorsFromDirectEntry: Visitors from Direct Entry

        

        - Referrers_visitorsFromDirectEntry_percent: Percent of Visitors from
          Direct Entry

        

        - Referrers_visitorsFromWebsites: Visitors from Websites

        

        - Referrers_visitorsFromWebsites_percent: Percent of Visitors from
          Websites

        

        - Referrers_visitorsFromCampaigns: Visitors from Campaigns

        

        - Referrers_visitorsFromCampaigns_percent: Percent of Visitors from
          Campaigns

        

        - Referrers_distinctSearchEngines: Distinct search engines

        

        - Referrers_distinctSocialNetworks: Distinct social networks

        

        - Referrers_distinctWebsites: Distinct websites

        

        - Referrers_distinctKeywords: Distinct keywords

        

        - Referrers_distinctCampaigns: Distinct campaigns

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.get&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.get&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.get&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.get&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getReferrerType(self, **qry_pars):
        """
        Channel Type

        ----------

        This table contains information about the distribution of the channel
        types.

        *Direct Entry:* A visitor has entered the URL in their browser and
        started browsing on your website - they entered the website directly.

        *Search Engines:* A visitor was referred to your website by a search
        engine.

        See the "Search Engines & Keywords" report for more details.

        *Websites:* The visitor followed a link on another website that led to
        your site.

        See the "Websites" report for more details.

        *Campaigns:* Visitors that came to your website as the result of a
        campaign.

        See the "Campaigns" report for more details.

        (dim: Channel Type / cat: Referrers / subcat: All Channels)

        ----------

        Parameters:

        idSite / period / date / segment / typeReferrer / idSubtable / expanded

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - _setReferrerTypeLabel=1

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getReferrerType&idSite=1&period=day&date=yesterday&_setReferrerTypeLabel=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getReferrerType&idSite=1&period=day&date=yesterday&_setReferrerTypeLabel=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getReferrerType&idSite=1&period=day&date=yesterday&_setReferrerTypeLabel=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getReferrerType&idSite=1&period=day&date=last10&_setReferrerTypeLabel=1&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAll(self, **qry_pars):
        """
        All Channels

        ----------

        This report shows all your Referrers in one unified report, listing all
        Websites, Search keywords and Campaigns used by your visitors to find
        your website.

        (dim: Referrer / cat: Referrers / subcat: All Channels)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getAll&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getAll&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getAll&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getAll&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywords(self, **qry_pars):
        """
        Keywords (including not defined)

        ----------

        This report shows which keywords users were searching for before they
        were referred to your website.

        By clicking on a row in the table, you can see the distribution of
        search engines that were queried for the keyword.

        Note: This report lists most keywords as not defined, because most
        search engines do not send the exact keyword used on the search engine.

        (dim: Keyword / cat: Referrers / subcat: Search Engines & Keywords)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getKeywords&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getKeywords&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getKeywords&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getKeywords&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSearchEnginesFromKeywordId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSearchEngines(self, **qry_pars):
        """
        Search Engines

        ----------

        This report shows which search engines referred users to your website.

        By clicking on a row in the table, you can see what users were searching
        for using a specific search engine.

        (dim: Search Engine / cat: Referrers / subcat: Search Engines &
        Keywords)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getSearchEngines&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getSearchEngines&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getSearchEngines&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getSearchEngines&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywordsFromSearchEngineId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCampaigns(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment / expanded

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getCampaigns&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getCampaigns&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getCampaigns&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getCampaigns&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywordsFromCampaignId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getWebsites(self, **qry_pars):
        """
        Websites

        ----------

        In this table, you can see which websites referred visitors to your
        site.

        By clicking on a row in the table, you can see which URLs the links to
        your website were on.

        (dim: Website / cat: Referrers / subcat: Websites)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getWebsites&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getWebsites&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getWebsites&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getWebsites&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUrlsFromWebsiteId(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / idSubtable / segment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSocials(self, **qry_pars):
        """
        Social Networks

        ----------

        In this table, you can see which websites referred visitors to your
        site.

        By clicking on a row in the table, you can see which URLs the links to
        your website were on.

        (dim: Social network / cat: Referrers / subcat: Social Networks)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / flat

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getSocials&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getSocials&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getSocials&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getSocials&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUrlsForSocial(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment / idSubtable

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getUrlsForSocial&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getUrlsForSocial&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getUrlsForSocial&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getUrlsForSocial&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNumberOfDistinctSearchEngines(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctSearchEngines&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctSearchEngines&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctSearchEngines&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctSearchEngines&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNumberOfDistinctSocialNetworks(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctSocialNetworks&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctSocialNetworks&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctSocialNetworks&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctSocialNetworks&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNumberOfDistinctKeywords(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctKeywords&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctKeywords&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctKeywords&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctKeywords&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNumberOfDistinctCampaigns(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctCampaigns&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctCampaigns&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctCampaigns&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctCampaigns&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNumberOfDistinctWebsites(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctWebsites&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctWebsites&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctWebsites&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctWebsites&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNumberOfDistinctWebsitesUrls(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctWebsitesUrls&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctWebsitesUrls&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctWebsitesUrls&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Referrers.getNumberOfDistinctWebsitesUrls&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModResolution:
    """
    This API module is not documented.
    """
    pass

    @method_decorator
    def getResolution(self, **qry_pars):
        """
        Screen Resolution

        ----------

        This report shows the screen resolutions your visitors used when viewing
        your website.

        (dim: Resolution / cat: Visitors / subcat: Devices)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Resolution.getResolution&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Resolution.getResolution&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Resolution.getResolution&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Resolution.getResolution&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getConfiguration(self, **qry_pars):
        """
        Configurations

        ----------

        This report shows the most common overall configurations that your
        visitors had. A configuration is the combination of an operating system,
        a browser type and a screen resolution.

        (dim: Configuration / cat: Visitors / subcat: Software)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Resolution.getConfiguration&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Resolution.getConfiguration&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Resolution.getConfiguration&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Resolution.getConfiguration&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModRollUpReporting:
    """
    API for plugin RollUpReporting
    """
    pass

    @method_decorator
    def addRollUp(self, **qry_pars):
        """
        Parameters:

        name / sourceIdSites / timezone / currency

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateRollUp(self, **qry_pars):
        """
        Parameters:

        idSite / name / sourceIdSites / timezone / currency

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=RollUpReporting.updateRollUp&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=RollUpReporting.updateRollUp&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=RollUpReporting.updateRollUp&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getRollUps(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=RollUpReporting.getRollUps&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=RollUpReporting.getRollUps&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=RollUpReporting.getRollUps&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModSEO:
    """
    The SEO API lets you access a list of SEO metrics for the specified URL:
    Google PageRank, Google/Bing indexed pages Alexa Rank and age of the Domain
    name.
    """
    pass

    @method_decorator
    def getRank(self, **qry_pars):
        """
        Parameters:

        url

        ----------

        Parameter examples:

        - url=https://divezone.net/

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SEO.getRank&url=https://divezone.net/&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SEO.getRank&url=https://divezone.net/&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SEO.getRank&url=https://divezone.net/&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModScheduledReports:
    """
    The ScheduledReports API lets you manage Scheduled Email reports, as well as
    generate, download or email any existing report. "generateReport" will
    generate the requested report (for a specific date range, website and in the
    requested language). "sendEmailReport" will send the report by email to the
    recipients specified for this report. You can also get the list of all
    existing reports via "getReports", create new reports via "addReport", or
    manage existing reports with "updateReport" and "deleteReport". See also the
    documentation about Scheduled Email reports in Matomo.
    """
    pass

    @method_decorator
    def addReport(self, **qry_pars):
        """
        Parameters:

        idSite / description / period / hour / reportType / reportFormat /
        reports / parameters / idSegment / evolutionPeriodFor / evolutionPeriodN
        / periodParam

        ----------

        Parameter examples:

        - evolutionPeriodFor=prev

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateReport(self, **qry_pars):
        """
        Parameters:

        idReport / idSite / description / period / hour / reportType /
        reportFormat / reports / parameters / idSegment / evolutionPeriodFor /
        evolutionPeriodN / periodParam

        ----------

        Parameter examples:

        - evolutionPeriodFor=prev

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteReport(self, **qry_pars):
        """
        Parameters:

        idReport

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getReports(self, **qry_pars):
        """
        Parameters:

        idSite / period / idReport / ifSuperUserReturnOnlySuperUserReports /
        idSegment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=ScheduledReports.getReports&idSite=1&period=day&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=ScheduledReports.getReports&idSite=1&period=day&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=ScheduledReports.getReports&idSite=1&period=day&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=ScheduledReports.getReports&idSite=1&period=day&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def generateReport(self, **qry_pars):
        """
        Parameters:

        idReport / date / language / outputType / period / reportFormat /
        parameters

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def sendReport(self, **qry_pars):
        """
        Parameters:

        idReport / period / date / force

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModSearchEngineKeywordsPerformance:
    """
    The SearchEngineKeywordsPerformance API lets you download all your SEO
    search keywords from Google, Bing & Yahoo and Yandex, as well as getting a
    detailed overview of how search robots crawl your websites and any error
    they may encounter.

    1) download all your search keywords as they were searched on Google, Bing &
    Yahoo and Yandex. This includes Google Images, Google Videos and Google
    News. This lets you view all keywords normally hidden from view behind
    "keyword not defined". With this plugin you can view them all!

    2) download all crawling overview stats and metrics from Bring and Yahoo and
    Google. Many metrics are available such as: Crawled pages, Crawl errors,
    Connection timeouts, HTTP-Status Code 301 (Permanently moved), HTTP-Status
    Code 400-499 (Request errors), All other HTTP-Status Codes, Total pages in
    index, Robots.txt exclusion, DNS failures, HTTP-Status Code 200-299,
    HTTP-Status Code 301 (Temporarily moved), HTTP-Status Code 500-599 (Internal
    server errors), Malware infected sites, Total inbound links.
    \Plugins\SearchEngineKeywordsPerformance
    """
    pass

    @method_decorator
    def getKeywords(self, **qry_pars):
        """
        Combined keywords

        ----------

        Report combining all keywords detected by Matomo and imported from
        search engines. This report only includes the visit metric. You can
        switch to one of the related report to get detailed metrics.

        (dim: Keyword / cat: Referrers / subcat: Search Engines & Keywords)

        ----------

        Parameters:

        idSite / period / date

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        This value appears only if you have set up 'Ecommerce Product/Category
        page tracking'. The number of visits on the Product/Category page.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywords&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywords&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywords&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywords&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywordsImported(self, **qry_pars):
        """
        Combined imported keywords

        ----------

        Report showing all keywords imported from all configured search engines.

        (dim: Keyword / cat: Referrers)

        ----------

        Parameters:

        idSite / period / date

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_clicks: Clicks

        A click is counted each time someone clicks on a link pointing to your
        website on a search engine results page.

        - nb_impressions: Impressions

        An impression is counted each time your website is displayed in a search
        engine results page.

        - ctr: CTR

        Clickthrough rate: A ratio showing how often people who see a search
        engine results page with a link to your website, end up clicking it.

        - position: Avg. position

        Average position of your website in the search engine results list (for
        this keyword).

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsImported&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsImported&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsImported&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsImported&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywordsGoogle(self, **qry_pars):
        """
        Parameters:

        idSite / period / date

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogle&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogle&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogle&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogle&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywordsBing(self, **qry_pars):
        """
        Keywords (on Bing and Yahoo!)

        ----------

        Keywords used in Bing or Yahoo! search that generated links to your
        website in the search results list.

        (dim: Keyword / cat: Referrers / subcat: Search Engines & Keywords)

        ----------

        Parameters:

        idSite / period / date

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_clicks: Clicks

        A click is counted each time someone clicks on a link pointing to your
        website on a search engine results page.

        - nb_impressions: Impressions

        An impression is counted each time your website is displayed in a search
        engine results page.

        - ctr: CTR

        Clickthrough rate: A ratio showing how often people who see a search
        engine results page with a link to your website, end up clicking it.

        - position: Avg. position

        Average position of your website in the search engine results list (for
        this keyword).

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsBing&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsBing&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsBing&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsBing&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywordsYandex(self, **qry_pars):
        """
        Parameters:

        idSite / period / date

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsYandex&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsYandex&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsYandex&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsYandex&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywordsGoogleWeb(self, **qry_pars):
        """
        Web keywords on Google

        ----------

        Keywords used in Google *web* search that generated links to your
        website in the search result list.

        (dim: Keyword / cat: Referrers / subcat: Search Engines & Keywords)

        ----------

        Parameters:

        idSite / period / date

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_clicks: Clicks

        A click is counted each time someone clicks on a link pointing to your
        website on a search engine results page.

        - nb_impressions: Impressions

        An impression is counted each time your website is displayed in a search
        engine results page.

        - ctr: CTR

        Clickthrough rate: A ratio showing how often people who see a search
        engine results page with a link to your website, end up clicking it.

        - position: Avg. position

        Average position of your website in the search engine results list (for
        this keyword).

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleWeb&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleWeb&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleWeb&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleWeb&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywordsGoogleImage(self, **qry_pars):
        """
        Image keywords on Google

        ----------

        Keywords used in Google *image* search that generated links to your
        website in the search result list.

        (dim: Keyword / cat: Referrers / subcat: Search Engines & Keywords)

        ----------

        Parameters:

        idSite / period / date

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_clicks: Clicks

        A click is counted each time someone clicks on a link pointing to your
        website on a search engine results page.

        - nb_impressions: Impressions

        An impression is counted each time your website is displayed in a search
        engine results page.

        - ctr: CTR

        Clickthrough rate: A ratio showing how often people who see a search
        engine results page with a link to your website, end up clicking it.

        - position: Avg. position

        Average position of your website in the search engine results list (for
        this keyword).

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleImage&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleImage&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleImage&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleImage&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywordsGoogleVideo(self, **qry_pars):
        """
        Video keywords on Google

        ----------

        Keywords used in Google *video* search that generated links to your
        website in the search result list.

        (dim: Keyword / cat: Referrers / subcat: Search Engines & Keywords)

        ----------

        Parameters:

        idSite / period / date

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_clicks: Clicks

        A click is counted each time someone clicks on a link pointing to your
        website on a search engine results page.

        - nb_impressions: Impressions

        An impression is counted each time your website is displayed in a search
        engine results page.

        - ctr: CTR

        Clickthrough rate: A ratio showing how often people who see a search
        engine results page with a link to your website, end up clicking it.

        - position: Avg. position

        Average position of your website in the search engine results list (for
        this keyword).

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleVideo&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleVideo&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleVideo&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleVideo&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeywordsGoogleNews(self, **qry_pars):
        """
        Parameters:

        idSite / period / date

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleNews&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleNews&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleNews&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getKeywordsGoogleNews&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCrawlingOverviewBing(self, **qry_pars):
        """
        Crawl overview for Bing and Yahoo!

        ----------

        The Crawl overview allows you to view crawl related information such as
        errors encountered by the search bot when visiting a page, items blocked
        by your robots.txt file and URLs potentially affected by malware.

        (cat: Referrers / subcat: Crawling overview)

        ----------

        Parameters:

        idSite / period / date

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getCrawlingOverviewBing&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getCrawlingOverviewBing&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getCrawlingOverviewBing&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getCrawlingOverviewBing&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCrawlingOverviewYandex(self, **qry_pars):
        """
        Parameters:

        idSite / period / date

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getCrawlingOverviewYandex&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getCrawlingOverviewYandex&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getCrawlingOverviewYandex&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getCrawlingOverviewYandex&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCrawlingErrorExamplesBing(self, **qry_pars):
        """
        Crawl errors on Bing

        ----------

        The report show crawling errors recently reported by Bing. It does not
        provide any historical data. Last updated May 21, 2021 00:07:21

        (cat: Actions / subcat: Crawling errors)

        ----------

        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getCrawlingErrorExamplesBing&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getCrawlingErrorExamplesBing&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SearchEngineKeywordsPerformance.getCrawlingErrorExamplesBing&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModSegmentEditor:
    """
    The SegmentEditor API lets you add, update, delete custom Segments, and list
    saved segments.
    """
    pass

    @method_decorator
    def isUserCanAddNewSegment(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SegmentEditor.isUserCanAddNewSegment&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SegmentEditor.isUserCanAddNewSegment&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SegmentEditor.isUserCanAddNewSegment&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def delete(self, **qry_pars):
        """
        Parameters:

        idSegment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def update(self, **qry_pars):
        """
        Parameters:

        idSegment / name / definition / idSite / autoArchive / enabledAllUsers

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def add(self, **qry_pars):
        """
        Parameters:

        name / definition / idSite / autoArchive / enabledAllUsers

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def get(self, **qry_pars):
        """
        Parameters:

        idSegment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAll(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SegmentEditor.getAll&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SegmentEditor.getAll&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SegmentEditor.getAll&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModSitesManager:
    """
    The SitesManager API gives you full control on Websites in Matomo (create,
    update and delete), and many methods to retrieve websites based on various
    attributes. This API lets you create websites via "addSite", update existing
    websites via "updateSite" and delete websites via "deleteSite". When
    creating websites, it can be useful to access internal codes used by Matomo
    for currencies via "getCurrencyList", or timezones via "getTimezonesList".
    There are also many ways to request a list of websites: from the website ID
    via "getSiteFromId" or the site URL via "getSitesIdFromSiteUrl". Often, the
    most useful technique is to list all websites that are known to a current
    user, based on the token_auth, via "getSitesWithAdminAccess",
    "getSitesWithViewAccess" or "getSitesWithAtLeastViewAccess" (which returns
    both). Some methods will affect all websites globally:
    "setGlobalExcludedIps" will set the list of IPs to be excluded on all
    websites, "setGlobalExcludedQueryParameters" will set the list of URL
    parameters to remove from URLs for all websites. The existing values can be
    fetched via "getExcludedIpsGlobal" and "getExcludedQueryParametersGlobal".
    See also the documentation about Managing Websites in Matomo.
    """
    pass

    @method_decorator
    def getJavascriptTag(self, **qry_pars):
        """
        Parameters:

        idSite / piwikUrl / mergeSubdomains / groupPageTitlesByDomain /
        mergeAliasUrls / visitorCustomVariables / pageCustomVariables /
        customCampaignNameQueryParam / customCampaignKeywordParam / doNotTrack /
        disableCookies / trackNoScript / crossDomain / forceMatomoEndpoint

        ----------

        Parameter examples:

        - idSite=1

        - piwikUrl=

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getJavascriptTag&idSite=1&piwikUrl=&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getJavascriptTag&idSite=1&piwikUrl=&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getJavascriptTag&idSite=1&piwikUrl=&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getImageTrackingCode(self, **qry_pars):
        """
        Parameters:

        idSite / piwikUrl / actionName / idGoal / revenue / forceMatomoEndpoint

        ----------

        Parameter examples:

        - idSite=1

        - piwikUrl=

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getImageTrackingCode&idSite=1&piwikUrl=&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getImageTrackingCode&idSite=1&piwikUrl=&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getImageTrackingCode&idSite=1&piwikUrl=&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesFromGroup(self, **qry_pars):
        """
        Parameters:

        group

        ----------

        Parameter examples:

        - group=

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesFromGroup&group=&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesFromGroup&group=&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesFromGroup&group=&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesGroups(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesGroups&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesGroups&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesGroups&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSiteFromId(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSiteFromId&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSiteFromId&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSiteFromId&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSiteUrlsFromId(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSiteUrlsFromId&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSiteUrlsFromId&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSiteUrlsFromId&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAllSites(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getAllSites&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getAllSites&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getAllSites&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAllSitesId(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getAllSitesId&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getAllSitesId&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getAllSitesId&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesWithAdminAccess(self, **qry_pars):
        """
        Parameters:

        fetchAliasUrls / pattern / limit

        ----------

        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesWithAdminAccess&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesWithAdminAccess&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesWithAdminAccess&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesWithViewAccess(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesWithViewAccess&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesWithViewAccess&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesWithViewAccess&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesWithAtLeastViewAccess(self, **qry_pars):
        """
        Parameters:

        limit

        ----------

        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesWithAtLeastViewAccess&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesWithAtLeastViewAccess&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesWithAtLeastViewAccess&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesIdWithAdminAccess(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithAdminAccess&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithAdminAccess&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithAdminAccess&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesIdWithViewAccess(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithViewAccess&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithViewAccess&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithViewAccess&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesIdWithWriteAccess(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithWriteAccess&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithWriteAccess&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithWriteAccess&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesIdWithAtLeastViewAccess(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithAtLeastViewAccess&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithAtLeastViewAccess&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdWithAtLeastViewAccess&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesIdFromSiteUrl(self, **qry_pars):
        """
        Parameters:

        url

        ----------

        Parameter examples:

        - url=https://divezone.net/

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdFromSiteUrl&url=https://divezone.net/&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdFromSiteUrl&url=https://divezone.net/&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSitesIdFromSiteUrl&url=https://divezone.net/&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addSite(self, **qry_pars):
        """
        Parameters:

        siteName / urls / ecommerce / siteSearch / searchKeywordParameters /
        searchCategoryParameters / excludedIps / excludedQueryParameters /
        timezone / currency / group / startDate / excludedUserAgents /
        keepURLFragments / type / settingValues / excludeUnknownUrls

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSiteSettings(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSiteSettings&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSiteSettings&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSiteSettings&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteSite(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addSiteAliasUrls(self, **qry_pars):
        """
        Parameters:

        idSite / urls

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setSiteAliasUrls(self, **qry_pars):
        """
        Parameters:

        idSite / urls (cs-list)

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.setSiteAliasUrls&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.setSiteAliasUrls&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.setSiteAliasUrls&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getIpsForRange(self, **qry_pars):
        """
        Parameters:

        ipRange

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setGlobalExcludedIps(self, **qry_pars):
        """
        Parameters:

        excludedIps

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setGlobalSearchParameters(self, **qry_pars):
        """
        Parameters:

        searchKeywordParameters / searchCategoryParameters

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSearchKeywordParametersGlobal(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSearchKeywordParametersGlobal&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSearchKeywordParametersGlobal&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSearchKeywordParametersGlobal&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSearchCategoryParametersGlobal(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSearchCategoryParametersGlobal&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSearchCategoryParametersGlobal&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getSearchCategoryParametersGlobal&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getExcludedQueryParametersGlobal(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getExcludedQueryParametersGlobal&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getExcludedQueryParametersGlobal&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getExcludedQueryParametersGlobal&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getExcludedUserAgentsGlobal(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getExcludedUserAgentsGlobal&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getExcludedUserAgentsGlobal&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getExcludedUserAgentsGlobal&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setGlobalExcludedUserAgents(self, **qry_pars):
        """
        Parameters:

        excludedUserAgents

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getKeepURLFragmentsGlobal(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getKeepURLFragmentsGlobal&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getKeepURLFragmentsGlobal&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getKeepURLFragmentsGlobal&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setKeepURLFragmentsGlobal(self, **qry_pars):
        """
        Parameters:

        enabled

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setGlobalExcludedQueryParameters(self, **qry_pars):
        """
        Parameters:

        excludedQueryParameters

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getExcludedIpsGlobal(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getExcludedIpsGlobal&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getExcludedIpsGlobal&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getExcludedIpsGlobal&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getDefaultCurrency(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getDefaultCurrency&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getDefaultCurrency&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getDefaultCurrency&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setDefaultCurrency(self, **qry_pars):
        """
        Parameters:

        defaultCurrency

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getDefaultTimezone(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getDefaultTimezone&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getDefaultTimezone&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getDefaultTimezone&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setDefaultTimezone(self, **qry_pars):
        """
        Parameters:

        defaultTimezone

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateSite(self, **qry_pars):
        """
        Parameters:

        idSite / siteName / urls / ecommerce / siteSearch /
        searchKeywordParameters / searchCategoryParameters / excludedIps /
        excludedQueryParameters / timezone / currency / group / startDate /
        excludedUserAgents / keepURLFragments / type / settingValues /
        excludeUnknownUrls

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCurrencyList(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getCurrencyList&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getCurrencyList&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getCurrencyList&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCurrencySymbols(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getCurrencySymbols&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getCurrencySymbols&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getCurrencySymbols&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def isTimezoneSupportEnabled(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.isTimezoneSupportEnabled&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.isTimezoneSupportEnabled&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.isTimezoneSupportEnabled&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getTimezonesList(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getTimezonesList&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getTimezonesList&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getTimezonesList&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getTimezoneName(self, **qry_pars):
        """
        Parameters:

        timezone / countryCode / multipleTimezonesInCountry

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUniqueSiteTimezones(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getUniqueSiteTimezones&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getUniqueSiteTimezones&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getUniqueSiteTimezones&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def renameGroup(self, **qry_pars):
        """
        Parameters:

        oldGroupName / newGroupName

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getPatternMatchSites(self, **qry_pars):
        """
        Parameters:

        pattern / limit

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNumWebsitesToDisplayPerPage(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getNumWebsitesToDisplayPerPage&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getNumWebsitesToDisplayPerPage&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=SitesManager.getNumWebsitesToDisplayPerPage&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModTagManager:
    """
    API for plugin Tag Manager. Lets you configure all your containers, create,
    update and delete tags, triggers, and variables. Create and publish new
    releases, enable and disable preview/debug mode, and much more. Please note:
    A container may have several versions. The current version that a user is
    editing is called the "draft" version. You can get the ID of the "draft"
    version by calling {@link TagManager.getContainer}.
    """
    pass

    @method_decorator
    def getAvailableContexts(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableContexts&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableContexts&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableContexts&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableEnvironments(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableEnvironments&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableEnvironments&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableEnvironments&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableEnvironmentsWithPublishCapability(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableEnvironmentsWithPublishCapability&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableEnvironmentsWithPublishCapability&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableEnvironmentsWithPublishCapability&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableTagFireLimits(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableTagFireLimits&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableTagFireLimits&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableTagFireLimits&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableComparisons(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableComparisons&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableComparisons&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=TagManager.getAvailableComparisons&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableTagTypesInContext(self, **qry_pars):
        """
        Parameters:

        idContext

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableTriggerTypesInContext(self, **qry_pars):
        """
        Parameters:

        idContext

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableVariableTypesInContext(self, **qry_pars):
        """
        Parameters:

        idContext

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerEmbedCode(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / environment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerInstallInstructions(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / environment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerTags(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def createDefaultContainerForSite(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=TagManager.createDefaultContainerForSite&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=TagManager.createDefaultContainerForSite&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=TagManager.createDefaultContainerForSite&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addContainerTag(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / type / name / parameters
        (cs-list) / fireTriggerIds (cs-list) / blockTriggerIds (cs-list) /
        fireLimit / fireDelay / priority / startDate / endDate

        ----------

        Parameter examples:

        - fireLimit=unlimited

        - fireDelay=0

        - priority=999

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateContainerTag(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / idTag / name / parameters
        (cs-list) / fireTriggerIds (cs-list) / blockTriggerIds (cs-list) /
        fireLimit / fireDelay / priority / startDate / endDate

        ----------

        Parameter examples:

        - fireLimit=unlimited

        - fireDelay=0

        - priority=999

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteContainerTag(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / idTag

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerTag(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / idTag

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerTriggerReferences(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / idTrigger

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerTriggers(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addContainerTrigger(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / type / name / parameters
        (cs-list) / conditions (cs-list)

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateContainerTrigger(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / idTrigger / name /
        parameters (cs-list) / conditions (cs-list)

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteContainerTrigger(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / idTrigger

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerTrigger(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / idTrigger

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerVariableReferences(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / idVariable

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerVariables(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableContainerVariables(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addContainerVariable(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / type / name / parameters
        (cs-list) / defaultValue / lookupTable (cs-list)

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateContainerVariable(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / idVariable / name /
        parameters (cs-list) / defaultValue / lookupTable (cs-list)

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteContainerVariable(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / idVariable

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerVariable(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / idVariable

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainers(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=TagManager.getContainers&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=TagManager.getContainers&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=TagManager.getContainers&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addContainer(self, **qry_pars):
        """
        Parameters:

        idSite / context / name / description

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateContainer(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / name / description

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def createContainerVersion(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / name / description / idContainerVersion

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateContainerVersion(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / name / description

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerVersions(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainerVersion(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteContainerVersion(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def publishContainerVersion(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion / environment

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteContainer(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContainer(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def enablePreviewMode(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def disablePreviewMode(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def exportContainerVersion(self, **qry_pars):
        """
        Parameters:

        idSite / idContainer / idContainerVersion

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def importContainerVersion(self, **qry_pars):
        """
        Parameters:

        exportedContainerVersion / idSite / idContainer / backupName

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModTour:
    """
    API for Tour plugin which helps you getting familiar with Matomo.
    """
    pass

    @method_decorator
    def getChallenges(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Tour.getChallenges&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Tour.getChallenges&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Tour.getChallenges&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def skipChallenge(self, **qry_pars):
        """
        Parameters:

        id

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getLevel(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Tour.getLevel&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Tour.getLevel&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Tour.getLevel&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModTransitions:
    """
    This API module is not documented.
    """
    pass

    @method_decorator
    def getTransitionsForPageTitle(self, **qry_pars):
        """
        Parameters:

        pageTitle / idSite / period / date / segment / limitBeforeGrouping

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getTransitionsForPageUrl(self, **qry_pars):
        """
        Parameters:

        pageUrl / idSite / period / date / segment / limitBeforeGrouping

        ----------

        Parameter examples:

        - pageUrl=https://divezone.net/

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Transitions.getTransitionsForPageUrl&pageUrl=https://divezone.net/&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Transitions.getTransitionsForPageUrl&pageUrl=https://divezone.net/&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Transitions.getTransitionsForPageUrl&pageUrl=https://divezone.net/&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=Transitions.getTransitionsForPageUrl&pageUrl=https://divezone.net/&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getTransitionsForAction(self, **qry_pars):
        """
        Parameters:

        actionName / actionType / idSite / period / date / segment /
        limitBeforeGrouping / parts

        ----------

        Parameter examples:

        - parts=all

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getTranslations(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=Transitions.getTranslations&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=Transitions.getTranslations&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=Transitions.getTranslations&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModTwoFactorAuth:
    """
    This API module is not documented.
    """
    pass

    @method_decorator
    def resetTwoFactorAuth(self, **qry_pars):
        """
        Parameters:

        userLogin

        ----------

        Parameter examples:

        - userLogin=test

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=TwoFactorAuth.resetTwoFactorAuth&userLogin=test&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=TwoFactorAuth.resetTwoFactorAuth&userLogin=test&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=TwoFactorAuth.resetTwoFactorAuth&userLogin=test&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModUserCountry:
    """
    The UserCountry API lets you access reports about your visitors' Countries
    and Continents.
    """
    pass

    @method_decorator
    def getCountry(self, **qry_pars):
        """
        Country

        ----------

        This report shows which country your visitors were in when they accessed
        your website.

        (dim: Country / cat: Visitors / subcat: Locations)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getCountry&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getCountry&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getCountry&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getCountry&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getContinent(self, **qry_pars):
        """
        Continent

        ----------

        This report shows which continent your visitors were in when they
        accessed your website.

        (dim: Continent / cat: Visitors / subcat: Locations)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getContinent&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getContinent&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getContinent&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getContinent&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getRegion(self, **qry_pars):
        """
        Region

        ----------

        This report shows which region your visitors were in when they accessed
        your website.

        In order to see data for this report, you must setup GeoIP in the
        Geolocation admin tab. The commercial `Maxmind
        <http://www.maxmind.com/?rId=piwik>`_ GeoIP databases are more accurate
        than the free ones. To see how accurate they are, click `here
        <http://www.maxmind.com/en/city_accuracy?rId=piwik>`_.

        (dim: Region / cat: Visitors / subcat: Locations)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getRegion&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getRegion&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getRegion&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getRegion&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCity(self, **qry_pars):
        """
        City

        ----------

        This report shows the cities your visitors were in when they accessed
        your website.

        In order to see data for this report, you must setup GeoIP in the
        Geolocation admin tab. The commercial `Maxmind
        <http://www.maxmind.com/?rId=piwik>`_ GeoIP databases are more accurate
        than the free ones. To see how accurate they are, click `here
        <http://www.maxmind.com/en/city_accuracy?rId=piwik>`_.

        (dim: City / cat: Visitors / subcat: Locations)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getCity&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getCity&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getCity&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getCity&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getCountryCodeMapping(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getCountryCodeMapping&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getCountryCodeMapping&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getCountryCodeMapping&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getLocationFromIP(self, **qry_pars):
        """
        Parameters:

        ip / provider

        ----------

        Parameter examples:

        - ip=194.57.91.215

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getLocationFromIP&ip=194.57.91.215&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getLocationFromIP&ip=194.57.91.215&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getLocationFromIP&ip=194.57.91.215&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setLocationProvider(self, **qry_pars):
        """
        Parameters:

        providerId

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNumberOfDistinctCountries(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getNumberOfDistinctCountries&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getNumberOfDistinctCountries&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getNumberOfDistinctCountries&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=UserCountry.getNumberOfDistinctCountries&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModUserId:
    """
    API for plugin UserId. Allows to get User IDs table.
    """
    pass

    @method_decorator
    def getUsers(self, **qry_pars):
        """
        User IDs

        ----------

        This report shows visits and other general metrics for every individual
        User ID.

        (dim: UserId / cat: Visitors / subcat: User IDs)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - label: Label

        

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_visits_converted: Visits with Conversions

        Number of visits that converted a goal.

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UserId.getUsers&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UserId.getUsers&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UserId.getUsers&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=UserId.getUsers&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModUserLanguage:
    """
    The UserLanguage API lets you access reports about your Visitors language
    setting
    """
    pass

    @method_decorator
    def getLanguage(self, **qry_pars):
        """
        Browser language

        ----------

        This report shows which language the visitor's browsers are using. (e.g.
        "English")

        (dim: Language / cat: Visitors / subcat: Locations)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UserLanguage.getLanguage&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UserLanguage.getLanguage&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UserLanguage.getLanguage&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=UserLanguage.getLanguage&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getLanguageCode(self, **qry_pars):
        """
        Language code

        ----------

        This report shows which exact language code the visitor's browsers is
        set to. (e.g. "German - Austria (de-at)")

        (dim: Language / cat: Visitors / subcat: Locations)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UserLanguage.getLanguageCode&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UserLanguage.getLanguageCode&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UserLanguage.getLanguageCode&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=UserLanguage.getLanguageCode&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModUsersFlow:
    """
    API for Users Flow. The API lets you explore details about how your users or
    visitors navigate through your website.
    """
    pass

    @method_decorator
    def getUsersFlowPretty(self, **qry_pars):
        """
        Users Flow

        ----------

        (dim: Interaction / cat: Actions)

        ----------

        Parameters:

        idSite / period / date / segment / expanded / flat / idSubtable /
        dataSource

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_exits: Exits

        The number of visits that did not leave after this interaction.

        - nb_proceeded: Proceeded

        The number of visits that proceeded to the next interaction and did not
        exit your website or app.

        - proceeded_rate: Proceeded Rate

        The percentage of visits that performed another interaction after
        performing an interaction.

        - exit_rate: Exit rate

        The percentage of visits that have left your website or app after this
        interaction.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersFlow.getUsersFlowPretty&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersFlow.getUsersFlowPretty&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersFlow.getUsersFlowPretty&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=UsersFlow.getUsersFlowPretty&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUsersFlow(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / limitActionsPerStep / exploreStep / exploreUrl
        / segment / expanded / dataSource

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - limitActionsPerStep=5

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersFlow.getUsersFlow&idSite=1&period=day&date=yesterday&limitActionsPerStep=5&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersFlow.getUsersFlow&idSite=1&period=day&date=yesterday&limitActionsPerStep=5&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersFlow.getUsersFlow&idSite=1&period=day&date=yesterday&limitActionsPerStep=5&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=UsersFlow.getUsersFlow&idSite=1&period=day&date=last10&limitActionsPerStep=5&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getInteractionActions(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / interactionPosition / offsetActionsPerStep /
        segment / idSubtable / dataSource

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableDataSources(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersFlow.getAvailableDataSources&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersFlow.getAvailableDataSources&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersFlow.getAvailableDataSources&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModUsersManager:
    """
    The UsersManager API lets you Manage Users and their permissions to access
    specific websites. You can create users via "addUser", update existing users
    via "updateUser" and delete users via "deleteUser". There are many ways to
    list users based on their login "getUser" and "getUsers", their email
    "getUserByEmail", or which users have permission (view or admin) to access
    the specified websites "getUsersWithSiteAccess". Existing Permissions are
    listed given a login via "getSitesAccessFromUser", or a website ID via
    "getUsersAccessFromSite", or you can list all users and websites for a given
    permission via "getUsersSitesFromAccess". Permissions are set and updated
    via the method "setUserAccess". See also the documentation about Managing
    Users in Matomo.
    """
    pass

    @method_decorator
    def getAvailableRoles(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getAvailableRoles&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getAvailableRoles&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getAvailableRoles&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getAvailableCapabilities(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getAvailableCapabilities&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getAvailableCapabilities&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getAvailableCapabilities&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setUserPreference(self, **qry_pars):
        """
        Parameters:

        userLogin / preferenceName / preferenceValue

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUserPreference(self, **qry_pars):
        """
        Parameters:

        preferenceName / userLogin

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUsersPlusRole(self, **qry_pars):
        """
        Parameters:

        idSite / limit / offset / filter_search / filter_access

        ----------

        Parameter examples:

        - idSite=1

        - offset=0

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersPlusRole&idSite=1&offset=0&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersPlusRole&idSite=1&offset=0&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersPlusRole&idSite=1&offset=0&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUsers(self, **qry_pars):
        """
        Parameters:

        userLogins

        ----------

        Parameter examples:

        - userLogins=

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsers&userLogins=&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsers&userLogins=&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsers&userLogins=&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUsersLogin(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersLogin&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersLogin&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersLogin&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUsersSitesFromAccess(self, **qry_pars):
        """
        Parameters:

        access

        ----------

        Parameter examples:

        - access=view

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersSitesFromAccess&access=view&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersSitesFromAccess&access=view&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersSitesFromAccess&access=view&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUsersAccessFromSite(self, **qry_pars):
        """
        Parameters:

        idSite

        ----------

        Parameter examples:

        - idSite=1

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersAccessFromSite&idSite=1&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersAccessFromSite&idSite=1&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersAccessFromSite&idSite=1&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUsersWithSiteAccess(self, **qry_pars):
        """
        Parameters:

        idSite / access

        ----------

        Parameter examples:

        - idSite=1

        - access=view

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersWithSiteAccess&idSite=1&access=view&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersWithSiteAccess&idSite=1&access=view&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersWithSiteAccess&idSite=1&access=view&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesAccessFromUser(self, **qry_pars):
        """
        Parameters:

        userLogin

        ----------

        Parameter examples:

        - userLogin=test

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getSitesAccessFromUser&userLogin=test&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getSitesAccessFromUser&userLogin=test&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getSitesAccessFromUser&userLogin=test&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSitesAccessForUser(self, **qry_pars):
        """
        Parameters:

        userLogin / limit / offset / filter_search / filter_access

        ----------

        Parameter examples:

        - userLogin=test

        - offset=0

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getSitesAccessForUser&userLogin=test&offset=0&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getSitesAccessForUser&userLogin=test&offset=0&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getSitesAccessForUser&userLogin=test&offset=0&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUser(self, **qry_pars):
        """
        Parameters:

        userLogin

        ----------

        Parameter examples:

        - userLogin=test

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUser&userLogin=test&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUser&userLogin=test&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUser&userLogin=test&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUserByEmail(self, **qry_pars):
        """
        Parameters:

        userEmail

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addUser(self, **qry_pars):
        """
        Parameters:

        userLogin / password / email / initialIdSite

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setSuperUserAccess(self, **qry_pars):
        """
        Parameters:

        userLogin / hasSuperUserAccess / passwordConfirmation

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def hasSuperUserAccess(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.hasSuperUserAccess&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.hasSuperUserAccess&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.hasSuperUserAccess&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUsersHavingSuperUserAccess(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersHavingSuperUserAccess&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersHavingSuperUserAccess&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.getUsersHavingSuperUserAccess&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def updateUser(self, **qry_pars):
        """
        Parameters:

        userLogin / password / email / passwordConfirmation

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def deleteUser(self, **qry_pars):
        """
        Parameters:

        userLogin

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def userExists(self, **qry_pars):
        """
        Parameters:

        userLogin

        ----------

        Parameter examples:

        - userLogin=test

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.userExists&userLogin=test&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.userExists&userLogin=test&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.userExists&userLogin=test&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def userEmailExists(self, **qry_pars):
        """
        Parameters:

        userEmail

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUserLoginFromUserEmail(self, **qry_pars):
        """
        Parameters:

        userEmail

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def setUserAccess(self, **qry_pars):
        """
        Parameters:

        userLogin / access / idSites

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def addCapabilities(self, **qry_pars):
        """
        Parameters:

        userLogin / capabilities / idSites

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def removeCapabilities(self, **qry_pars):
        """
        Parameters:

        userLogin / capabilities / idSites

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def createAppSpecificTokenAuth(self, **qry_pars):
        """
        Parameters:

        userLogin / passwordConfirmation / description / expireDate /
        expireHours

        ----------

        Parameter examples:

        - expireHours=0

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def newsletterSignup(self, **qry_pars):
        """
        Parameter examples:

        - format=xml / format=json / format=tsv

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=UsersManager.newsletterSignup&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=UsersManager.newsletterSignup&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=UsersManager.newsletterSignup&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModVisitFrequency:
    """
    VisitFrequency API lets you access a list of metrics related to Returning
    Visitors.
    """
    pass

    @method_decorator
    def get(self, **qry_pars):
        """
        Returning Visits

        ----------

        This report shows general metrics like visits for returning visitors
        side by side with the same metrics for new visitors. Learn how returning
        visitors perform overall compared to new visitors.

        (cat: Actions / subcat: Engagement)

        ----------

        Parameters:

        idSite / period / date / segment / columns

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits_returning: Returning Visits

        

        - nb_actions_returning: Actions by Returning Visits

        

        - nb_uniq_visitors_returning: Unique returning visitors

        

        - nb_users_returning: Returning Users

        

        - max_actions_returning: Maximum actions in one returning visit

        

        - nb_visits_new: New Visits

        

        - nb_actions_new: Actions by New Visits

        

        - nb_uniq_visitors_new: Unique new visitors

        

        - nb_users_new: New Users

        

        - max_actions_new: max_actions_new

        

        - avg_time_on_site_returning: Avg. Duration of a Returning Visit (in
          sec)

        

        - nb_actions_per_visit_returning: Avg. Actions per Returning Visit

        

        - bounce_rate_returning: Bounce Rate for Returning Visits

        

        - avg_time_on_site_new: Avg. Duration of a New Visit (in sec)

        

        - nb_actions_per_visit_new: Avg. Actions per New Visit

        

        - bounce_rate_new: Bounce Rate for New Visits

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitFrequency.get&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitFrequency.get&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitFrequency.get&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitFrequency.get&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModVisitTime:
    """
    VisitTime API lets you access reports by Hour (Server time), and by Hour
    Local Time of your visitors.
    """
    pass

    @method_decorator
    def getVisitInformationPerLocalTime(self, **qry_pars):
        """
        Visits per local time

        ----------

        This graph shows what time it was in the *visitors' time zones* during
        their visits.

        (dim: Local time - hour (Start of visit) / cat: Visitors / subcat:
        Times)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getVisitInformationPerLocalTime&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getVisitInformationPerLocalTime&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getVisitInformationPerLocalTime&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getVisitInformationPerLocalTime&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getVisitInformationPerServerTime(self, **qry_pars):
        """
        Visits per server time

        ----------

        This graph shows what time it was in the *server's time zone* during the
        visits.

        (dim: Server time - hour (Start of visit) / cat: Visitors / subcat:
        Times)

        ----------

        Parameters:

        idSite / period / date / segment / hideFutureHoursWhenToday

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_conversions: Conversions

        Number of goal conversions.

        - revenue: Revenue

        The total revenue generated by Product sales. Excludes tax, shipping and
        discount.

        - revenue_per_visit: Revenue per Visit

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getVisitInformationPerServerTime&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getVisitInformationPerServerTime&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getVisitInformationPerServerTime&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getVisitInformationPerServerTime&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getByDayOfWeek(self, **qry_pars):
        """
        Visits by Day of Week

        ----------

        This graph shows the number of visits your website received on each day
        of the week.

        (dim: Day of the week / cat: Visitors / subcat: Times)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Time on Website

        The average duration of a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - conversion_rate: Conversion Rate

        The percentage of visits that triggered a goal conversion.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getByDayOfWeek&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getByDayOfWeek&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getByDayOfWeek&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitTime.getByDayOfWeek&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModVisitorInterest:
    """
    VisitorInterest API lets you access two Visitor Engagement reports: number
    of visits per number of pages, and number of visits per visit duration.
    """
    pass

    @method_decorator
    def getNumberOfVisitsPerVisitDuration(self, **qry_pars):
        """
        Length of Visits

        ----------

        In this report, you can see how many visits had a certain total
        duration. Initially, the report is shown as a tag cloud, more common
        durations are displayed in a larger font.

        Please note, that you can view the report in other ways than as a tag
        cloud. Use the controls at the bottom of the report to do so.

        (dim: Visit duration / cat: Actions / subcat: Engagement)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsPerVisitDuration&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsPerVisitDuration&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsPerVisitDuration&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsPerVisitDuration&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNumberOfVisitsPerPage(self, **qry_pars):
        """
        Pages per Visit

        ----------

        In this report, you can see how many visits involved a certain number of
        pageviews. Initially, the report is shown as a tag cloud, more common
        numbers of pages are displayed in a larger font.

        Please note, that you can view the report in other ways than as a tag
        cloud. Use the controls at the bottom of the report to do so.

        (dim: Pages per visit / cat: Actions / subcat: Engagement)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsPerPage&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsPerPage&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsPerPage&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsPerPage&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNumberOfVisitsByDaysSinceLast(self, **qry_pars):
        """
        Visits by days since last visit

        ----------

        In this report, you can see how many visits were from visitors whose
        last visit was a certain number of days ago.

        (dim: Days since last visit / cat: Actions / subcat: Engagement)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsByDaysSinceLast&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsByDaysSinceLast&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsByDaysSinceLast&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsByDaysSinceLast&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getNumberOfVisitsByVisitCount(self, **qry_pars):
        """
        Visits by Visit Number

        ----------

        In this report, you can see the number of visits who were the Nth visit,
        ie. visitors who visited your website at least N times.

        Please note, that you can view the report in other ways than as a tag
        cloud. Use the controls at the bottom of the report to do so.

        (dim: Visits by Visit Number / cat: Actions / subcat: Engagement)

        ----------

        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_visits_percentage: % Visits

        

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsByVisitCount&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsByVisitCount&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsByVisitCount&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitorInterest.getNumberOfVisitsByVisitCount&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
@module_decorator
class ModVisitsSummary:
    """
    VisitsSummary API lets you access the core web analytics metrics (visits,
    unique visitors, count of actions (page views & downloads & clicks on
    outlinks), time on site, bounces and converted visits.
    """
    pass

    @method_decorator
    def get(self, **qry_pars):
        """
        Visits Summary

        ----------

        This report provides a very general overview of how your visitors
        behave.

        (cat: Visitors / subcat: Overview)

        ----------

        Parameters:

        idSite / period / date / segment / columns

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Metrics:

        - nb_uniq_visitors: Unique visitors

        The number of unduplicated visitors coming to your website. Every user
        is only counted once, even if they visit the website multiple times a
        day.

        - nb_visits: Visits

        If a visitor comes to your website for the first time or if they visit a
        page more than 30 minutes after their last page view, this will be
        recorded as a new visit.

        - nb_users: Users

        The number of users logged in your website. It is the number of unique
        active users that have a User ID set (via the Tracking code function
        'setUserId').

        - nb_actions: Actions

        The number of actions performed by your visitors. Actions can be page
        views, internal site searches, downloads or outlinks.

        - max_actions: Maximum actions in one visit

        Maximum number of actions in a visit.

        - bounce_rate: Bounce Rate

        The percentage of visits that only had a single pageview. This means,
        that the visitor left the website directly from the entrance page.

        - nb_actions_per_visit: Actions per Visit

        The average number of actions (page views, site searches, downloads or
        outlinks) that were performed during the visits.

        - avg_time_on_site: Avg. Visit Duration (in seconds)

        The average duration of a visit.

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.get&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.get&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.get&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.get&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getVisits(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getVisits&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getVisits&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getVisits&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getVisits&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUniqueVisitors(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getUniqueVisitors&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getUniqueVisitors&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getUniqueVisitors&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getUniqueVisitors&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getUsers(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getUsers&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getUsers&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getUsers&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getUsers&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getActions(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getActions&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getActions&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getActions&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getActions&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getMaxActions(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getMaxActions&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getMaxActions&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getMaxActions&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getMaxActions&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getBounceCount(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getBounceCount&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getBounceCount&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getBounceCount&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getBounceCount&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getVisitsConverted(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getVisitsConverted&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getVisitsConverted&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getVisitsConverted&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getVisitsConverted&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSumVisitsLength(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getSumVisitsLength&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getSumVisitsLength&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getSumVisitsLength&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getSumVisitsLength&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    @method_decorator
    def getSumVisitsLengthPretty(self, **qry_pars):
        """
        Parameters:

        idSite / period / date / segment

        ----------

        Parameter examples:

        - idSite=1

        - period=day

        - date=yesterday / date=last10

        - format=xml / format=json / format=tsv / format=rss

        - translateColumnNames=1

        ----------

        Example url requests:

        `xml
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getSumVisitsLengthPretty&idSite=1&period=day&date=yesterday&format=xml&token_auth=anonymous>`_,
        `json
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getSumVisitsLengthPretty&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous>`_,
        `tsv
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getSumVisitsLengthPretty&idSite=1&period=day&date=yesterday&format=Tsv&token_auth=anonymous&translateColumnNames=1>`_,
        `rss
        <https://demo.matomo.cloud/?module=API&method=VisitsSummary.getSumVisitsLengthPretty&idSite=1&period=day&date=last10&format=rss&token_auth=anonymous&translateColumnNames=1>`_

        ----------

        :param qry_pars: parameters of the API Query

        :type qry_pars: QryDict

        :return: API Query response

        :rtype: Response
        """
        return qry_pars

    
