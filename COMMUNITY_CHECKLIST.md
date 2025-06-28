# SmartCARS Central - Community Checklist

## 🎯 Problem: "Invalid credentials" może być związane z Community settings

**Community:** Topsky (ID: 618)  
**API Endpoint:** https://dtopsky.topsky.app/acars/api/

## ✅ Checklist SmartCARS Central:

### 1. **Login to SmartCARS Central**
- [ ] Idź do: https://smartcars.central  
- [ ] Zaloguj się swoim kontem
- [ ] Znajdź Community "Topsky" (ID: 618)

### 2. **Community Status Check**
- [ ] Status: **ACTIVE** ✅ / INACTIVE ❌
- [ ] Community Type: Virtual Airline / Organization
- [ ] Moderator Status: Approved / Pending / Rejected
- [ ] Members Count: > 0

### 3. **API Configuration Check**
- [ ] API URL: `https://dtopsky.topsky.app/acars/api/`
- [ ] API Type: phpVMS 7 / phpVMS 5 / Custom API
- [ ] API Status: Enabled / Disabled
- [ ] API Test: Passed / Failed

### 4. **Permissions Check**  
- [ ] Your Role: Owner / Administrator / Moderator
- [ ] API Permissions: Full Access / Limited / None
- [ ] Community Settings Access: Yes / No

### 5. **Advanced Settings**
- [ ] ACARS Integration: Enabled / Disabled
- [ ] Flight Center: Enabled / Disabled  
- [ ] Custom Plugins: Any restrictions?
- [ ] API Version: v3.0 compatible?

## 🔧 **Typowe Problemy i Rozwiązania:**

### Problem A: Community Inactive
```
Rozwiązanie:
1. Contact SmartCARS Central support
2. Request community reactivation
3. Provide proper documentation
```

### Problem B: Wrong API URL in Central
```
Obecny URL w Central: [sprawdź]
Poprawny URL: https://dtopsky.topsky.app/acars/api/

Rozwiązanie:
1. Update API URL w Community settings
2. Test API connection w Central
3. Save changes
```

### Problem C: API Type Mismatch
```
Sprawdź API Type w Central:
- Jeśli "phpVMS 5" → zmień na "phpVMS 7"
- Jeśli "Custom" → sprawdź compatibility settings
```

### Problem D: Pending Approvals
```
Sprawdź czy są:
- Pending API approvals
- Pending community changes
- Pending moderator reviews

Rozwiązanie: Contact support for approval
```

## 📞 **SmartCARS Central Support:**

Jeśli problemy persistują:

1. **Contact Info:**
   - Support Portal: SmartCARS Central Help
   - Discord: TFDi Design Discord  
   - Email: support kontakt

2. **Information to Provide:**
   - Community ID: 618
   - Community Name: Topsky
   - API URL: https://dtopsky.topsky.app/acars/api/
   - Problem: "Invalid credentials" w SmartCARS 3 client
   - Your role w Community

3. **Logs to Include:**
   - SmartCARS client logs
   - API test results (nasze testy są OK)
   - Screenshots z Central configuration

## 🎯 **Quick Test After Changes:**

Po każdej zmianie w SmartCARS Central:

1. **Logout/Login w SmartCARS 3 client**
2. **Refresh Community list**
3. **Re-enter credentials**
4. **Test connection**

## ⚡ **Alternative Solution:**

Jeśli Community settings są OK, spróbuj:

1. **Create NEW Community** (temporalne)
2. **Test z new Community ID**  
3. **Jeśli działa → problem był w old Community**
4. **Jeśli nie działa → problem jest gdzie indziej**

---

**Remember:** Nasze Django API działa w 100% - problem jest w SmartCARS ecosystem configuration! 