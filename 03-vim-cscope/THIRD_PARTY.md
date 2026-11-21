# Third-party components

The copy of each bundled package includes the license from the identified
upstream revision.

| Bundled package | Upstream revision | License |
| --- | --- | --- |
| [fzf.vim](https://github.com/junegunn/fzf.vim/tree/fe5f1fd45418c1a4d905f44a59357008058cc789) | fe5f1fd45418c1a4d905f44a59357008058cc789 | [MIT](.vim/pack/workbench/start/fzf.vim/LICENSE) |
| [Tagbar](https://github.com/preservim/tagbar/tree/07cb8247487208124978daff8e13624667635457) | 07cb8247487208124978daff8e13624667635457 | [Tagbar's Vim-based license](.vim/pack/workbench/start/tagbar/LICENSE) |
| [vim-airline](https://github.com/vim-airline/vim-airline/tree/8dc1bd0a116de527f6bc58c1d04386ba357c624f) | 8dc1bd0a116de527f6bc58c1d04386ba357c624f | [MIT](.vim/pack/workbench/start/vim-airline/LICENSE) |
| [vim-airline-themes](https://github.com/vim-airline/vim-airline-themes/tree/77aab8c6cf7179ddb8a05741da7e358a86b2c3ab) | 77aab8c6cf7179ddb8a05741da7e358a86b2c3ab | [MIT](.vim/pack/workbench/start/vim-airline-themes/LICENSE) |
| [vim-bookmarks](https://github.com/MattesGroeger/vim-bookmarks/tree/93904787c61805334895662feb6672a9164820be) | 93904787c61805334895662feb6672a9164820be | [MIT](.vim/pack/workbench/start/vim-bookmarks/LICENSE) |

The workbench bundles the vim-bookmarks Vim scripts, upstream README, and
license. The packaged scripts match the ones used in the demonstration.

The bootstrap fetches these dependencies into the ignored .deps directory.

- fzf 0.75.0 uses the pinned upstream revision
  4499615fe9c06c0651aa5650e5d0d0a5face99a8. Its source and executable
  come from upstream. [fzf license](https://github.com/junegunn/fzf/blob/4499615fe9c06c0651aa5650e5d0d0a5face99a8/LICENSE)
- Gruvbox uses revision ef8864bb42bf244f0295d1c5a403b27e3d139695.
  The upstream README identifies MIT/X11. [Gruvbox license notice](https://github.com/morhetz/gruvbox/tree/ef8864bb42bf244f0295d1c5a403b27e3d139695#license)
