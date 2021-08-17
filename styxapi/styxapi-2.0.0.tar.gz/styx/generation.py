from textwrap import dedent
import re

from jinja2 import Environment, StrictUndefined

from .types import to_ts


env = Environment()
env.filters['has_body'] = lambda value: value in ['post', 'patch', 'put']
env.filters['to_ts'] = to_ts
env.filters['path_to_placeholder'] = lambda value: re.sub(
        '\\{([ a-zA-Z_]+)\\}', lambda m: '${ ' + m.groups()[0] + ' }', value)

env.undefined = StrictUndefined


api_template = env.from_string(dedent("""
    import { Observable } from 'rxjs';
    import { map } from 'rxjs/operators';
    import { ajax } from 'rxjs/ajax';

    type Param = string | number | undefined | null;

    function encodeParams(params: {[name: string]: Param}): string {
        return Object
            .keys(params)
            .filter(key => params[key] !== null && params[key] !== undefined)
            .map(key => `${ key }=${ encodeURIComponent(params[key]!) }`)
            .join('&');
    }

    {% for name, type in styx.types.items() %}
    export type {{ name }} = {{ type | to_ts }};
    {% endfor %}

    export class Api {
    {% for operation in styx.operations %}
        public {{ operation.operation_id }}(
            {%- for param in operation.parameters -%}
                {{ param.name }}: any,
            {%- endfor -%}
            {%- if operation.method | has_body -%}
                body: {{ operation.body_type | to_ts }}
            {%- endif -%}
        ): Observable<{{ operation.response_type | to_ts }}> {
            const url = `{{ operation.path | path_to_placeholder }}?${ encodeParams({
                {%- for param in operation.parameters -%}
                    {%- if param.in == 'query' -%}
                        {{ param.name }},
                    {%- endif -%}
                {%- endfor -%}
            }) }`;
            {%- if operation.method | has_body %}
            return ajax
                .{{ operation.method }}<any>(
                    url,
                    JSON.stringify(body),
                    {'Content-Type': 'application/json'})
                .pipe(map(r => r.response))
            {% else %}
            return ajax
                .{{ operation.method }}<any>(url)
                .pipe(map(r => r.response))
            {%- endif %}
        }
    {% endfor %}
    }

    export const api = new Api();

"""))
