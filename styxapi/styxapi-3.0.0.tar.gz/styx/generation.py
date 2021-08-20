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
    import { Observable, from } from 'rxjs';
    import { map, concatMap } from 'rxjs/operators';
    import { ajax } from 'rxjs/ajax';
    import { fromFetch } from 'rxjs/fetch';

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

        protected request(method: string, url: string, body?: any): Observable<any> {
          const options = {
            method: method.toUpperCase(),
            ...(body !== undefined
                ? {
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(body)
                }
                : {}
            )
          }

          return fromFetch(new Request(url, options)).pipe(
            concatMap(r => from(r.json())));
        }

        protected requestX(method: string, url: string, body?: any): Observable<any> {
            if (body === undefined) {
                return ajax({ url, method: method.toUpperCase() })
                    .pipe(map(r => r.response));
            }
            else {
                return ajax({
                    url,
                    method: method.toUpperCase(),
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                }).pipe(map(r => r.response));;
            }
        }

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
            return this.request({{ operation.method | tojson }}, url, body);
            {% else %}
            return this.request({{ operation.method | tojson }}, url);
            {%- endif %}
        }
    {% endfor %}
    }

    export const api = new Api();

"""))
