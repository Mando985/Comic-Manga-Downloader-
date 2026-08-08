# nhentai API v2.0.0

Base URL: `https://nhentai.net/api/v2`
OpenAPI spec: `/api/v2/openapi.json`

## Authentication

- Generate an API key in account settings.
- Pass it as: `Authorization: Key YOUR_API_KEY`
- Set a descriptive `User-Agent` header: `AppName/version (contact or project URL)`

## CDN Rules

- Gallery and thumbnail paths are **relative**; fetch CDN servers from `GET /api/v2/cdn` and concatenate one with the path.
- **Do not** hardcode subdomains.
- **Do not** construct paths by guessing extensions, suffixes, or numbering. Use the path exactly as returned.
- Invalid patterns result in silent rejection → repeated violations → extended ban.
- Rate limits are generous; brief bursts are fine. Sustained high rates → temporary ban. Treat `429` as backoff.
- Use `POST /api/v2/galleries/{id}/download` for full-gallery archives. Don't reconstruct by walking page URLs on the CDN.

## Endpoints

### General

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2` | Api Root |
| GET | `/api/v2/pow` | Get PoW Challenge |
| GET | `/api/v2/config` | Get Config |
| GET | `/api/v2/captcha` | Get Captcha Info |
| GET | `/api/v2/cdn` | Get CDN Config |

### Galleries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/galleries` | Get All Galleries |
| GET | `/api/v2/galleries/tagged` | Get Galleries By Tag |
| GET | `/api/v2/galleries/popular` | Get Popular Galleries |
| GET | `/api/v2/galleries/random` | Get Random Gallery |
| GET | `/api/v2/galleries/{gallery_id}` | Get Gallery |
| GET | `/api/v2/galleries/{gallery_id}/related` | Get Related Galleries |
| GET | `/api/v2/galleries/{gallery_id}/favorite` | Check Favorite |
| POST | `/api/v2/galleries/{gallery_id}/favorite` | Add To Favorites |
| DELETE | `/api/v2/galleries/{gallery_id}/favorite` | Remove From Favorites |
| POST | `/api/v2/galleries/{gallery_id}/edit` | Submit Gallery Edit |
| POST | `/api/v2/galleries/{gallery_id}/download` | Get download URL for a gallery |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/search` | Search Galleries (full-text with filters) |

### Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/tags/ids` | Get Tags By Ids |
| POST | `/api/v2/tags/search` | Search Tags |
| GET | `/api/v2/tags/{tag_type}` | Get Tags By Type |
| GET | `/api/v2/tags/{tag_type}/{slug}` | Get Tag By Slug |

### Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/galleries/{gallery_id}/comments` | Get Gallery Comments |
| POST | `/api/v2/galleries/{gallery_id}/comments` | Create Comment |
| GET | `/api/v2/galleries/{gallery_id}/comments/count` | Get Comment Count |
| DELETE | `/api/v2/comments/{comment_id}` | Delete Comment |
| POST | `/api/v2/comments/{comment_id}/flag` | Flag Comment |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/users/{user_id}/{slug}` | Get User Profile |

### Favorites

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/favorites` | Get Favorites |
| GET | `/api/v2/favorites/random` | Get Random Favorite |

### Blacklist

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/blacklist` | Get Blacklist |
| POST | `/api/v2/blacklist` | Update Blacklist |
| GET | `/api/v2/blacklist/ids` | Get Blacklist Ids |

### Zones

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/zones` | Get Zones |
| GET | `/api/v2/zones/i` | Get Popunder Inventory |
| POST | `/api/v2/zones/h` | Record Popunder Hit |
| GET | `/api/v2/zones/pu` | Popunder Redirect |

### GTS (Gallery Tag Suggestions)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/galleries/{gallery_id}/suggestions` | List Suggestions |
| POST | `/api/v2/galleries/{gallery_id}/suggestions` | Create Suggestion |
| GET | `/api/v2/gts/backlog` | List GTS Backlog |
| GET | `/api/v2/gts/new-tags` | List New Tag Index |
| POST | `/api/v2/galleries/{gallery_id}/suggestions/{suggestion_id}/vote` | Vote On Suggestion |
| DELETE | `/api/v2/galleries/{gallery_id}/suggestions/{suggestion_id}` | Withdraw Suggestion |

### Taxonomy

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/taxonomy` | List Taxonomy Suggestions |
| POST | `/api/v2/taxonomy` | Create Taxonomy Suggestion |
| GET | `/api/v2/taxonomy/stats` | Get Taxonomy Suggestion Stats |
| GET | `/api/v2/taxonomy/resolved` | List Resolved Taxonomy Suggestions |
| GET | `/api/v2/taxonomy/{suggestion_id}` | Get Taxonomy Suggestion |
| DELETE | `/api/v2/taxonomy/{suggestion_id}` | Withdraw Taxonomy Suggestion |
| GET | `/api/v2/taxonomy/{suggestion_id}/comments` | List Taxonomy Comments |
| POST | `/api/v2/taxonomy/{suggestion_id}/comments` | Create Taxonomy Comment |
| DELETE | `/api/v2/taxonomy/{suggestion_id}/comments/{comment_id}` | Delete Taxonomy Comment |
| POST | `/api/v2/taxonomy/{suggestion_id}/vote` | Vote On Taxonomy Suggestion |

### First-party / Internal Only (NOT for third-party clients)

Third-party apps must use API key auth (`Authorization: Key YOUR_API_KEY`). These are for nhentai's own services:

**User:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/user` | Get Me |
| PUT | `/api/v2/user` | Update Profile |
| DELETE | `/api/v2/user` | Delete Account |
| POST | `/api/v2/user/avatar` | Upload Avatar |
| GET | `/api/v2/user/keys` | List API Keys |
| POST | `/api/v2/user/keys` | Create API Key |
| DELETE | `/api/v2/user/keys/{key_id}` | Revoke API Key |

**Auth:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v2/auth/login` | Login |
| POST | `/api/v2/auth/register` | Register |
| POST | `/api/v2/auth/refresh` | Refresh |
| POST | `/api/v2/auth/logout` | Logout |
| POST | `/api/v2/auth/logout/all` | Logout All |
| GET | `/api/v2/auth/sessions` | Get Sessions |
| DELETE | `/api/v2/auth/sessions/{session_id}` | Revoke Session |
| POST | `/api/v2/auth/reset` | Request Password Reset |
| POST | `/api/v2/auth/reset/confirm` | Confirm Password Reset |

### Moderation (Staff-only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/moderation/users/{user_id}` | Get User Mod Info |
| DELETE | `/api/v2/moderation/users/{user_id}` | Delete User |
| PUT | `/api/v2/moderation/users/{user_id}/shadowban` | Shadowban User |
| DELETE | `/api/v2/moderation/users/{user_id}/shadowban` | Unshadowban User |
| GET | `/api/v2/moderation/galleries/hidden` | List Hidden Galleries |
| GET | `/api/v2/moderation/galleries/{gallery_id}` | Get Gallery Mod Info |
| PUT | `/api/v2/moderation/galleries/{gallery_id}/hidden` | Hide Gallery |
| DELETE | `/api/v2/moderation/galleries/{gallery_id}/hidden` | Unhide Gallery |
| POST | `/api/v2/comments/flags/{flag_id}/review` | Review Comment Flag |
| GET | `/api/v2/moderation/flags` | Get Pending Flags |
| GET | `/api/v2/moderation/edits` | Get Pending Edits |
| GET | `/api/v2/moderation/edits/{edit_id}` | Get Edit |
| POST | `/api/v2/moderation/edits/{edit_id}/vote` | Vote On Edit |
| POST | `/api/v2/moderation/edits/{edit_id}/apply` | Apply Edit |
| POST | `/api/v2/moderation/edits/{edit_id}/reject` | Reject Edit |
| GET | `/api/v2/moderation/comments/recent` | Get Recent Comments |
| GET | `/api/v2/moderation/comments/spam` | Get Spam Comments |
| PUT | `/api/v2/moderation/comments/{comment_id}/hide` | Hide Comment |
| DELETE | `/api/v2/moderation/comments/{comment_id}/hide` | Unhide Comment |
| POST | `/api/v2/moderation/bulk/hide` | Bulk Hide |
| POST | `/api/v2/moderation/bulk/unhide` | Bulk Unhide |
| POST | `/api/v2/moderation/bulk/shadowban` | Bulk Shadowban |
| POST | `/api/v2/moderation/bulk/unshadowban` | Bulk Unshadowban |
| GET | `/api/v2/moderation/api-keys` | List All API Keys |
| DELETE | `/api/v2/moderation/api-keys/{key_id}` | Revoke API Key Admin |
| GET | `/api/v2/moderation/spam/config` | Get Spam Config |
| PUT | `/api/v2/moderation/spam/config/{name}` | Update Spam Config |
| POST | `/api/v2/moderation/gts/{suggestion_id}/accept` | Accept Suggestion |
| POST | `/api/v2/moderation/gts/{suggestion_id}/reject` | Reject Suggestion |
| POST | `/api/v2/moderation/gts/{suggestion_id}/revert` | Revert Suggestion |
| POST | `/api/v2/moderation/tags` | Moderation Create Tag |
| POST | `/api/v2/moderation/taxonomy/{suggestion_id}/accept` | Accept Taxonomy Suggestion |
| DELETE | `/api/v2/moderation/taxonomy/{suggestion_id}` | Delete Taxonomy Suggestion |
| POST | `/api/v2/moderation/taxonomy/{suggestion_id}/reject` | Reject Taxonomy Suggestion |

## Key Schemas

- `GalleryDetailResponse`, `GalleryListItem` — gallery objects
- `GalleryTitle` — gallery title (object with fields like `english`, `japanese`, `pretty`)
- `CommentResponse`, `PaginatedResponse[CommentResponse]` — comments
- `TagResponse`, `TagPaginatedResponse` — tags
- `UserInfo`, `UserProfileResponse`, `UserMeResponse`, `UserPublic` — users
- `FavoriteResponse`, `RecentFavorite` — favorites
- `BlacklistResponse`, `BlacklistUpdateRequest` — blacklist
- `DownloadResponse` — download URL
- `CdnConfigResponse` — CDN server list
- `ConfigResponse`, `CaptchaInfoResponse`, `PoWChallengeResponse` — config/challenge
- `ErrorResponse`, `HTTPValidationError`, `ValidationError` — errors
- `SuggestionResponse`, `SuggestionListResponse`, `GallerySuggestionsBundle` — GTS
- `TaxonomySuggestionResponse`, `TaxonomySuggestionListResponse` — taxonomy
- `ZonesResponse`, `CreativeSlot`, `HtmlSlot`, `PopunderInventoryResponse` — ad zones
- `ModerationUserInfo`, `ModerationGalleryInfo`, `ModerationCommentResponse`, etc. — moderation
- `SessionListItem`, `TokenResponse`, `RefreshResponse` — auth
- `ApiKeyListItem`, `ApiKeyCreateResponse` — API keys
- `Announcement`, `AnnouncementLink` — announcements
