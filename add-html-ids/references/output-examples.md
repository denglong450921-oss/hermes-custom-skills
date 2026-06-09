# add_html_ids.py — Output examples

## Context-based naming (OLD — DO NOT USE)

Previous versions used parent-context chains, producing IDs like:

```html
<div id="support_footer_col7" class="footer-column">
  <div id="support_footer_help_title" class="footer-column__title">Help & Support</div>
  <ul id="support_footer_help_list" class="footer-column__list">
    <li id="support_footer_help_center">
      <a id="support_svg_path_path_path_path_path_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a_a"
         href="https://support.ecwid.com/">Help Center</a>
    </li>
  </ul>
</div>
```

The `<a>` tag ID was over 120 characters long because it traced every ancestor (footer → inner → columns → col7 → list → li → a). Unusable.

## Flat naming (CURRENT — fixed)

Now produces clean IDs via `{prefix}_{hint}`:

```html
<div id="support_footer_col7" class="footer-column">
  <div id="support_footer_help_title" class="footer-column__title">Help & Support</div>
  <ul id="support_footer_help_list" class="footer-column__list">
    <li id="support_footer_help_list_li">
      <a id="support_footer_link_help" href="https://support.ecwid.com/">Help Center</a>
    </li>
  </ul>
</div>
```

HTML elements: `support_link`, `support_link_2`, `support_path`, `support_path_2`, etc.
TSX components: `home_header`, `home_herosection`, `home_img`, `home_img_2`, etc.
