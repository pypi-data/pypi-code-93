'''
    Copyright 2018 SerialLab, CORP

    This file is part of SerialBox.

    SerialBox is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SerialBox is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with SerialBox.  If not, see <http://www.gnu.org/licenses/>.
'''
import logging

from django.utils.translation import ugettext_lazy as _

from rest_framework.permissions import BasePermission
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.throttling import UserRateThrottle
from rest_framework import generics, views, exceptions, status
from rest_framework.exceptions import NotFound
from serialbox.api import serializers as sb_serializers
from serialbox.discovery import get_generator
from serialbox.flavor_packs import FlavorSaver
from serialbox.rules.steps import execute_rule_inline
from serialbox.models import ResponseRule
from rest_framework.permissions import IsAuthenticated

from quartet_capture.models import Task as DBTask, TaskParameter

logger = logging.getLogger(__name__)


class AllocationPermission(BasePermission):
    """
    Checks to see if users have the right to allocate numbers.
    """

    def has_permission(self, request, view):
        """
        Super users and allocate_numbers permission holders are allowed.
        """
        return request.user.has_perm('serialbox.allocate_numbers') or \
               request.user.is_superuser


class APIRoot(views.APIView):
    '''
    ## Welcome!

    The SerialBox Number Pool API is written using
    [Django](http://djangoproject.com) and the
    [The Django Rest Framework](http://http://www.django-rest-framework.org/).
    If you familliar with using the Django Rest
    Framework then you will know how to configure the system to use different
    types of paging and formatting options, etc.  For more information on
    Django and the Django Rest Frameowork see:

    * [The Django Project](http://djangoproject.com)
    * [The Django Rest Framework](http://http://www.django-rest-framework.org/)

    '''
    permission_classes = (IsAuthenticated,)

    response_list = [
        'pool-list',
        'pool-create',
        'sequential-region-list',
        'sequential-region-create',
        'allocate']

    def __init__(self, **kwargs):
        views.APIView.__init__(self, **kwargs)
        self.response = Response()
        self.response_list += FlavorSaver.get_api_urls()

    def get(self, request):
        response_dict = {
        }
        for item in self.response_list:
            response_dict[item] = reverse(item, request=request)
        self.response.data = response_dict
        return self.response

    def get_view_name(self):
        return _('SerialBox Number Pool API')

    def _get_api_list(self):
        '''
        Returns the api_list from any installed flavor packs.
        '''
        pass

    class Meta(object):
        verbose_name = _('SerialBox Number Pool API')


class DetailViewBase(generics.RetrieveAPIView):
    throttle_classes = (UserRateThrottle,)


class AllocateView(views.APIView):
    '''
    ## Description

    The Pool Request View is the primary view by which other systems will
    access the API for Pool and Region number allocation requests.

    ## Usage
    The url should be formatted as follows:

    ###Format
    ```
    http[s]://[servername]:[port]/allocate/[pool machine-name]/[size
    of the request]/?format=[format]
    ```

    So, for example, to request 1000 numbers from a SerialBox pool with machine
    name *my-foo-bar* in JSON
    formatting, on the host *www.foobar.com*, one would do the following:
    ----
    ###Example
    ```
    http[s]://www.foobar.com/allocate/my-foo-bar/1000/?format=json
    ```

    **Note**: Paging is not active for this view since the number list is an
    attribute of the response.
    ---
    ##Response Example

    ###JSON Response
    By default, the only Django Rest Framework response format enabled is JSON.
    If you want to enable XML and/or CSV, see the Django Rest Framework
    documentation to modify your Django settings file.

    ```
    {
    "numbers": "[395, 404]",
    "fulfilled": true,
    "type": "",
    "encoding": "decimal",
    "pool": "Pool One",
    "region": "Test Region Two",
    "size_granted": 10,
    "remote_host": "localhost:8000"
    }
    ```
    ### Values

    * __numbers__:  This field will contain the numbers returned
    from the request.
    Depending on the nature of the request, this field may have two numbers as
    in the case of a response to request for numbers from a sequential Pool.
    Specifically, in the case of a Sequential Pool, the first number returned
    will be the starting number of a range and the second number in the list
    will be the last in the range. For example, *[1,100]* would mean the first
    number was 1 and the last number was 100.  The receiving client would then
    be responsible for issuing out the numbers between 1 and 100 to another
    system, etc.  In the case of a response that would return a list, such as
    a random request, every number of the response
    (list length equal to the inbound
    *size* parameter) will be included in the list.  So, for example, a request
    for 100 random numbers would result in the list containing 100 numbers.
    Keeping this in mind, it would be prudent to throttle request sizes
    to an amount reasonable for both the requesting and receiving systems in
    any architecture.
    * __fulfilled__:  A boolean value which lets the
    calling system know whether
    or not the full request size has been met.  For example,
    if a calling system
    requests 100 numbers but the SerialBox Pool handling the request only had
    50 left to give out, the 50 would be returned with the __fullfilled__ flag
    set to _false_.
    * __type__:  A value corresponding to the type of response being returned.
    the possoble values are:
        * sequential - two numbers are returned the *first* and *last* in a
        range.
        * random - a full list of random numbers who's length is equal in size
        to the size parameter in the request (unless the fulfilled return value
        is false).
        * list - a list of numbers in, potentially, any order.
    * __encoding__: The encoding of the numeric data- either:
        * base-36 - 0 through 9, a through z.
        * hex - hexadecimal
        * decimal - 0 through 9
    * __region__: The *machine name* of the region that handled the response
    via the Pool specified in the request.
    '''
    permission_classes = (IsAuthenticated, AllocationPermission)
    serializer_class = sb_serializers.ResponseSerializer

    def get(self, request: Request, pool=None, size=None, region=None):
        try:
            ret = []
            # TODO: doing this so I can display the documentation page without
            # generating an error.  Probably want a better approach
            if pool and size:
                logger.debug('Request received for pool %s and region %s.')
                # convert the size parameter to an integer
                size = int(size)

                generator = get_generator(pool)
                # pass the request off to the generator
                response = generator.get_response(request, size,
                                                  pool, region)
                response_rule = None
                try:
                    content_type = request.accepted_renderer.format
                    response_rule = ResponseRule.objects.get(
                        content_type=content_type,
                        pool=generator.pool
                    )
                except ResponseRule.DoesNotExist:
                    logger.info("No response rules for content type %s and "
                                "pool %s", request.accepted_renderer.format,
                                generator.pool)

                if not response_rule:
                    serializer = sb_serializers.ResponseSerializer(response)
                    ret = serializer.data
                    response.save()
                else:
                    # get the response rule that matches the content
                    logger.debug('looking for a responserule with format %s '
                                 'for pool %s.', format,
                                 generator.pool.readable_name)
                    db_task = self._set_task_parameters(pool, region,
                                                        response_rule, size,
                                                        request)
                    try:
                        number_list = response.get_number_list()
                        rule = execute_rule_inline(number_list, db_task)
                        ret = rule.data
                        db_task.STATUS = "FINISHED"
                        db_task.save()
                        response.task_name = db_task.name
                        response.save()
                    except ResponseRule.DoesNotExist:
                        db_task.status = 'ERROR'
                        db_task.save()
                        logger.exception(
                            'Could not find a response rule for this '
                            'format. Falling back to default return '
                            'value')
                        raise
            return Response(ret)
        except NotFound:
            raise
        except Exception as e:
            raise exceptions.APIException(
                str(e),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _set_task_parameters(self, pool, region, response_rule, size, request):
        db_task = DBTask.objects.create(
            rule=response_rule.rule,
            status='FINISHED'
        )
        TaskParameter.objects.create(
            name='source',
            value='serialbox-allocate',
            task=db_task
        )
        TaskParameter.objects.create(
            name='pool',
            value=pool,
            task=db_task
        )
        TaskParameter.objects.create(
            name='size',
            value=str(size),
            task=db_task
        )
        if region:
            TaskParameter.objects.create(
                name='region',
                value=region,
                task=db_task
            )
        query_values = request.query_params.dict()
        if len(query_values) > 0:
            for k, v in query_values.items():
                TaskParameter.objects.create(
                    name=k,
                    value=v,
                    task=db_task
                )

        return db_task
