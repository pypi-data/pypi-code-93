import os
import streamlit.components.v1 as components
import streamlit as st


# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    st.set_page_config(
        page_title="Flash Card custom component example", page_icon=":coin:", layout="wide"
    )

    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "flash_card",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3001",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("flash_card", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def flash_card(
    title,
    primary_text,
    secondary_text=None,
    formatter="0,0",
    aspect_ratio=[16, 9],
    key=None,
):
    """Create a new instance of "flash_card".

    Parameters
    ----------
    name: str
        The name of the thing we're saying hello to. The component will display
        the text "Hello, {name}!"
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    int
        The number of times the component's "Click Me" button has been clicked.
        (This is the value passed to `Streamlit.setComponentValue` on the
        frontend.)

    """

    st.subheader(title)

    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    component_value = _component_func(
        title=title,
        aspectRatio=aspect_ratio,
        formatter=formatter,
        primaryText=primary_text,
        secondaryText=secondary_text,
        key=key,
        default=0,
    )

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value


# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/__init__.py`
if not _RELEASE:

    # Create a second instance of our component whose `name` arg will vary
    # based on a text_input widget.
    #
    # We use the special "key" argument to assign a fixed identity to this
    # component instance. By default, when a component's arguments change,
    # it is considered a new instance and will be re-mounted on the frontend
    # and lose its current state. In this case, we want to vary the component's
    # "name" argument without having it get recreated.
    with st.sidebar:
        title = st.text_input("Enter a title", value="LPT Total Supply")
        primary_text = st.text_input("Enter primary text", value="23701711.68")
        formatter = st.text_input("Number format", value="0,0.00a")
        st.write("Format reference: http://numeraljs.com/#format")
        secondary_text = st.text_input("Enter secondary text", value="LPT")

    st.title("Responsive/theme-able flash card examples")

    c1, c2 = st.columns([3, 2])

    with c1:
        st.header("16:9")
        st.markdown(
            flash_card(
                title,
                primary_text=primary_text,
                secondary_text=secondary_text,
                formatter=formatter,
                key="normal",
            )
        )

    with c2:
        st.header("4:3")
        st.markdown(
            flash_card(
                title,
                primary_text=primary_text,
                secondary_text=secondary_text,
                formatter=formatter,
                aspect_ratio=[4, 3],
                key="four_by_three",
            )
        )

    c11, c12 = st.columns([1, 2])
    with c11:
        st.header("1:1")
        st.markdown(
            flash_card(
                title,
                primary_text=primary_text,
                secondary_text=secondary_text,
                formatter=formatter,
                aspect_ratio=[1, 1],
                key="square1",
            )
        )
    with c12:
        st.header("2:1")
        st.markdown(
            flash_card(
                title,
                primary_text=primary_text,
                secondary_text=secondary_text,
                formatter=formatter,
                aspect_ratio=[2, 1],
                key="square2",
            )
        )
